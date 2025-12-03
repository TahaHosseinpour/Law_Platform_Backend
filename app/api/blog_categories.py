from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from prisma.models import User
from app.core.deps import get_db, require_permission
from app.core.permissions import Permission
from app.schemas.blog import (
    BlogCategoryCreate,
    BlogCategoryUpdate,
    BlogCategoryResponse
)

router = APIRouter(prefix="/blog-categories", tags=["Blog Categories"])


@router.post("/", response_model=BlogCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: BlogCategoryCreate,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_BLOG))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Create a new blog category (admin/lawyer only)"""
    # Check if category with same slug exists
    existing = await db.blogcategory.find_unique(where={"slug": category_data.slug})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists"
        )

    category = await db.blogcategory.create(
        data={
            "name": category_data.name,
            "slug": category_data.slug,
            "description": category_data.description,
        }
    )

    return category


@router.get("/", response_model=list[BlogCategoryResponse])
async def get_all_categories(
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """Get all blog categories (public)"""
    categories = await db.blogcategory.find_many(
        skip=skip,
        take=limit,
        order={"name": "asc"}
    )

    return categories


@router.get("/{category_id}", response_model=BlogCategoryResponse)
async def get_category_by_id(
    category_id: int,
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get blog category by ID (public)"""
    category = await db.blogcategory.find_unique(where={"id": category_id})

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.get("/slug/{slug}", response_model=BlogCategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get blog category by slug (public)"""
    category = await db.blogcategory.find_unique(where={"slug": slug})

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.put("/{category_id}", response_model=BlogCategoryResponse)
async def update_category(
    category_id: int,
    category_update: BlogCategoryUpdate,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_BLOG))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Update blog category (admin/lawyer only)"""
    category = await db.blogcategory.find_unique(where={"id": category_id})

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if new slug conflicts
    if category_update.slug and category_update.slug != category.slug:
        existing = await db.blogcategory.find_unique(where={"slug": category_update.slug})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists"
            )

    update_data = category_update.model_dump(exclude_unset=True)
    updated_category = await db.blogcategory.update(
        where={"id": category_id},
        data=update_data
    )

    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_BLOG))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Delete blog category (admin only)"""
    category = await db.blogcategory.find_unique(where={"id": category_id})

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if category has posts
    posts = await db.blogpost.count(where={"categoryId": category_id})
    if posts > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with existing posts"
        )

    await db.blogcategory.delete(where={"id": category_id})

    return None
