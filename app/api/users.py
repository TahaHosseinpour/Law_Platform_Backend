from typing import Annotated
from fastapi import APIRouter, Depends
from prisma import Prisma
from prisma.models import User
from app.core.deps import get_db, get_current_user, require_permission
from app.core.permissions import Permission
from app.core.security import get_password_hash
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(require_permission(Permission.UPDATE_OWN_PROFILE))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Update current user profile"""
    update_data = user_update.model_dump(exclude_unset=True)

    # Hash password if provided
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    # Update user
    updated_user = await db.user.update(
        where={"id": current_user.id},
        data=update_data
    )

    return updated_user
