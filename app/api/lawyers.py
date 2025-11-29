from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from prisma.models import User
from app.core.deps import get_db, get_current_user, require_permission, require_role
from app.core.permissions import Permission, UserRole
from app.schemas.lawyer import LawyerProfileCreate, LawyerProfileUpdate, LawyerProfileResponse

router = APIRouter(prefix="/lawyers", tags=["Lawyers"])


@router.post("/profile", response_model=LawyerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_lawyer_profile(
    profile_data: LawyerProfileCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.LAWYER))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Create lawyer profile (only for lawyers)"""
    # Check if profile already exists
    existing_profile = await db.lawyerprofile.find_unique(where={"userId": current_user.id})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lawyer profile already exists"
        )

    # Create profile
    profile = await db.lawyerprofile.create(
        data={
            "userId": current_user.id,
            "licenseNumber": profile_data.licenseNumber,
            "specialization": profile_data.specialization,
            "experienceYears": profile_data.experienceYears,
            "bio": profile_data.bio,
            "phoneNumber": profile_data.phoneNumber,
            "address": profile_data.address,
        }
    )

    return profile


@router.get("/profile/me", response_model=LawyerProfileResponse)
async def get_my_lawyer_profile(
    current_user: Annotated[User, Depends(require_role(UserRole.LAWYER))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get current lawyer's profile"""
    profile = await db.lawyerprofile.find_unique(where={"userId": current_user.id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )

    return profile


@router.put("/profile/me", response_model=LawyerProfileResponse)
async def update_my_lawyer_profile(
    profile_update: LawyerProfileUpdate,
    current_user: Annotated[User, Depends(require_permission(Permission.UPDATE_LAWYER_PROFILE))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Update current lawyer's profile"""
    # Check if profile exists
    existing_profile = await db.lawyerprofile.find_unique(where={"userId": current_user.id})
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )

    # Update profile
    update_data = profile_update.model_dump(exclude_unset=True)
    updated_profile = await db.lawyerprofile.update(
        where={"userId": current_user.id},
        data=update_data
    )

    return updated_profile


@router.get("/", response_model=list[LawyerProfileResponse])
async def get_all_lawyers(
    current_user: Annotated[User, Depends(require_permission(Permission.VIEW_LAWYER_PROFILES))],
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
    verified_only: bool = False
):
    """Get all lawyer profiles (with pagination)"""
    where_clause = {"isVerified": True} if verified_only else {}

    profiles = await db.lawyerprofile.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        order={"createdAt": "desc"}
    )

    return profiles


@router.get("/{lawyer_id}", response_model=LawyerProfileResponse)
async def get_lawyer_by_id(
    lawyer_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.VIEW_LAWYER_PROFILES))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get lawyer profile by ID"""
    profile = await db.lawyerprofile.find_unique(where={"id": lawyer_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )

    return profile
