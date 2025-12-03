from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from prisma.models import User
from datetime import datetime
from app.core.deps import get_db, get_current_user, require_permission
from app.core.permissions import Permission
from app.schemas.blog import (
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostResponse
)

router = APIRouter(prefix="/blog-posts", tags=["Blog Posts"])


@router.post("/", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: BlogPostCreate,
    current_user: Annotated[User, Depends(require_permission(Permission.CREATE_BLOG_POST))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Create a new blog post (admin/lawyer only)"""
    # Check if category exists
    category = await db.blogcategory.find_unique(where={"id": post_data.categoryId})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if slug is unique
    existing = await db.blogpost.find_unique(where={"slug": post_data.slug})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this slug already exists"
        )

    # Set published date if post is published
    published_at = datetime.utcnow() if post_data.isPublished else None

    post = await db.blogpost.create(
        data={
            "categoryId": post_data.categoryId,
            "authorId": current_user.id,
            "title": post_data.title,
            "slug": post_data.slug,
            "content": post_data.content,
            "excerpt": post_data.excerpt,
            "featuredImage": post_data.featuredImage,
            "isPublished": post_data.isPublished,
            "publishedAt": published_at,
        }
    )

    return post


@router.get("/", response_model=list[BlogPostResponse])
async def get_all_posts(
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 20,
    published_only: bool = True,
    category_id: int = None
):
    """Get all blog posts (public)"""
    where_clause = {}

    if published_only:
        where_clause["isPublished"] = True

    if category_id:
        where_clause["categoryId"] = category_id

    posts = await db.blogpost.find_many(
        where=where_clause if where_clause else None,
        skip=skip,
        take=limit,
        order={"publishedAt": "desc"}
    )

    return posts


@router.get("/{post_id}", response_model=BlogPostResponse)
async def get_post_by_id(
    post_id: int,
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get blog post by ID (public)"""
    post = await db.blogpost.find_unique(where={"id": post_id})

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Increment view count
    await db.blogpost.update(
        where={"id": post_id},
        data={"viewCount": post.viewCount + 1}
    )

    return post


@router.get("/slug/{slug}", response_model=BlogPostResponse)
async def get_post_by_slug(
    slug: str,
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get blog post by slug (public)"""
    post = await db.blogpost.find_unique(where={"slug": slug})

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Increment view count
    await db.blogpost.update(
        where={"slug": slug},
        data={"viewCount": post.viewCount + 1}
    )

    return post


@router.get("/my-posts/", response_model=list[BlogPostResponse])
async def get_my_posts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 50
):
    """Get current user's blog posts"""
    posts = await db.blogpost.find_many(
        where={"authorId": current_user.id},
        skip=skip,
        take=limit,
        order={"createdAt": "desc"}
    )

    return posts


@router.put("/{post_id}", response_model=BlogPostResponse)
async def update_post(
    post_id: int,
    post_update: BlogPostUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Update blog post"""
    post = await db.blogpost.find_unique(where={"id": post_id})

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Check if user is author or admin
    if post.authorId != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )

    # Check if new slug conflicts
    if post_update.slug and post_update.slug != post.slug:
        existing = await db.blogpost.find_unique(where={"slug": post_update.slug})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post with this slug already exists"
            )

    update_data = post_update.model_dump(exclude_unset=True)

    # Set published date if publishing for the first time
    if post_update.isPublished and not post.isPublished:
        update_data["publishedAt"] = datetime.utcnow()

    updated_post = await db.blogpost.update(
        where={"id": post_id},
        data=update_data
    )

    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Delete blog post"""
    post = await db.blogpost.find_unique(where={"id": post_id})

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Check if user is author or admin
    if post.authorId != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    await db.blogpost.delete(where={"id": post_id})

    return None
