from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    """Transaction types"""
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"


class TransactionStatus(str, Enum):
    """Transaction status"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TransactionBase(BaseModel):
    """Base transaction schema"""
    amount: Decimal
    type: TransactionType
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Transaction creation schema"""
    pass


class TransactionUpdate(BaseModel):
    """Transaction update schema (admin only)"""
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Transaction response schema"""
    id: int
    userId: int
    status: TransactionStatus
    referenceId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
