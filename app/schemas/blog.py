from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BlogCategoryBase(BaseModel):
    """Base blog category schema"""
    name: str
    slug: str
    description: Optional[str] = None


class BlogCategoryCreate(BlogCategoryBase):
    """Blog category creation schema"""
    pass


class BlogCategoryUpdate(BaseModel):
    """Blog category update schema"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None


class BlogCategoryResponse(BlogCategoryBase):
    """Blog category response schema"""
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class BlogPostBase(BaseModel):
    """Base blog post schema"""
    categoryId: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    featuredImage: Optional[str] = None
    isPublished: bool = False


class BlogPostCreate(BlogPostBase):
    """Blog post creation schema"""
    pass


class BlogPostUpdate(BaseModel):
    """Blog post update schema"""
    categoryId: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featuredImage: Optional[str] = None
    isPublished: Optional[bool] = None


class BlogPostResponse(BlogPostBase):
    """Blog post response schema"""
    id: int
    authorId: int
    publishedAt: Optional[datetime] = None
    viewCount: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
