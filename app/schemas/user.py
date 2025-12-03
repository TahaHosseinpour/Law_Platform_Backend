from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.core.permissions import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    fullName: str


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    fullName: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRole
    isActive: bool
    credit: Decimal
    avatar: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
