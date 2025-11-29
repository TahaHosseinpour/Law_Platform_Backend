from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LawyerProfileBase(BaseModel):
    """Base lawyer profile schema"""
    licenseNumber: str
    specialization: str
    experienceYears: int
    bio: Optional[str] = None
    phoneNumber: Optional[str] = None
    address: Optional[str] = None


class LawyerProfileCreate(LawyerProfileBase):
    """Lawyer profile creation schema"""
    pass


class LawyerProfileUpdate(BaseModel):
    """Lawyer profile update schema"""
    licenseNumber: Optional[str] = None
    specialization: Optional[str] = None
    experienceYears: Optional[int] = None
    bio: Optional[str] = None
    phoneNumber: Optional[str] = None
    address: Optional[str] = None


class LawyerProfileResponse(LawyerProfileBase):
    """Lawyer profile response schema"""
    id: int
    userId: int
    isVerified: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
