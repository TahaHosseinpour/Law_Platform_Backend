from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from prisma.models import User
from app.core.deps import get_db, require_permission
from app.core.permissions import Permission
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_USERS))],
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """Get all users (admin only)"""
    users = await db.user.find_many(
        skip=skip,
        take=limit,
        order={"createdAt": "desc"}
    )

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_USERS))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get user by ID (admin only)"""
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.DELETE_USERS))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Delete user (admin only)"""
    # Check if user exists
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    # Delete user
    await db.user.delete(where={"id": user_id})

    return None


@router.patch("/lawyers/{lawyer_id}/verify", status_code=status.HTTP_200_OK)
async def verify_lawyer(
    lawyer_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_LAWYERS))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Verify a lawyer profile (admin only)"""
    # Check if lawyer profile exists
    profile = await db.lawyerprofile.find_unique(where={"id": lawyer_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )

    # Verify lawyer
    updated_profile = await db.lawyerprofile.update(
        where={"id": lawyer_id},
        data={"isVerified": True}
    )

    return {"message": "Lawyer verified successfully", "profile": updated_profile}


@router.patch("/lawyers/{lawyer_id}/unverify", status_code=status.HTTP_200_OK)
async def unverify_lawyer(
    lawyer_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_LAWYERS))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Unverify a lawyer profile (admin only)"""
    # Check if lawyer profile exists
    profile = await db.lawyerprofile.find_unique(where={"id": lawyer_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )

    # Unverify lawyer
    updated_profile = await db.lawyerprofile.update(
        where={"id": lawyer_id},
        data={"isVerified": False}
    )

    return {"message": "Lawyer unverified successfully", "profile": updated_profile}
