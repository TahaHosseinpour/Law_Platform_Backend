from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from app.core.deps import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[Prisma, Depends(get_db)]
):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.user.find_unique(where={"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    user = await db.user.create(
        data={
            "email": user_data.email,
            "password": hashed_password,
            "fullName": user_data.fullName,
            "role": user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
        }
    )

    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Annotated[Prisma, Depends(get_db)]
):
    """Login and get access token"""
    # Find user
    user = await db.user.find_unique(where={"email": login_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token)
