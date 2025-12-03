from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from prisma.models import User
from app.core.deps import get_db, get_current_user, require_permission
from app.core.permissions import Permission
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionStatus
)
from decimal import Decimal
import uuid

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Create a new transaction"""
    # Generate unique reference ID
    reference_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    # Create transaction
    transaction = await db.transaction.create(
        data={
            "userId": current_user.id,
            "amount": transaction_data.amount,
            "type": transaction_data.type,
            "description": transaction_data.description,
            "referenceId": reference_id,
            "status": TransactionStatus.PENDING.value,
        }
    )

    return transaction


@router.get("/my-transactions", response_model=list[TransactionResponse])
async def get_my_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 50
):
    """Get current user's transactions"""
    transactions = await db.transaction.find_many(
        where={"userId": current_user.id},
        skip=skip,
        take=limit,
        order={"createdAt": "desc"}
    )

    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get transaction by ID"""
    transaction = await db.transaction.find_unique(where={"id": transaction_id})

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Check if user owns this transaction or is admin
    if transaction.userId != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this transaction"
        )

    return transaction


@router.patch("/{transaction_id}/complete", response_model=TransactionResponse)
async def complete_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_TRANSACTIONS))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Complete a transaction (admin only)"""
    transaction = await db.transaction.find_unique(where={"id": transaction_id})

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    if transaction.status != TransactionStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete transaction with status: {transaction.status}"
        )

    # Update user credit based on transaction type
    user = await db.user.find_unique(where={"id": transaction.userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_credit = user.credit
    if transaction.type == "DEPOSIT" or transaction.type == "REFUND":
        new_credit += transaction.amount
    elif transaction.type == "WITHDRAW" or transaction.type == "PAYMENT":
        new_credit -= transaction.amount
        if new_credit < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient credit"
            )

    # Update user credit and transaction status
    await db.user.update(
        where={"id": transaction.userId},
        data={"credit": new_credit}
    )

    updated_transaction = await db.transaction.update(
        where={"id": transaction_id},
        data={"status": TransactionStatus.COMPLETED.value}
    )

    return updated_transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: Annotated[User, Depends(require_permission(Permission.MANAGE_TRANSACTIONS))],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Update transaction (admin only)"""
    transaction = await db.transaction.find_unique(where={"id": transaction_id})

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    update_data = transaction_update.model_dump(exclude_unset=True)

    updated_transaction = await db.transaction.update(
        where={"id": transaction_id},
        data=update_data
    )

    return updated_transaction


@router.get("/", response_model=list[TransactionResponse])
async def get_all_transactions(
    current_user: Annotated[User, Depends(require_permission(Permission.VIEW_ALL_DATA))],
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """Get all transactions (admin only)"""
    transactions = await db.transaction.find_many(
        skip=skip,
        take=limit,
        order={"createdAt": "desc"}
    )

    return transactions
