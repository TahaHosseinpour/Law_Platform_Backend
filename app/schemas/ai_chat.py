from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    """Message role"""
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class AIChatBase(BaseModel):
    """Base AI chat schema"""
    title: str


class AIChatCreate(AIChatBase):
    """AI chat creation schema"""
    pass


class AIChatUpdate(BaseModel):
    """AI chat update schema"""
    title: Optional[str] = None


class AIChatResponse(AIChatBase):
    """AI chat response schema"""
    id: int
    userId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class AIChatMessageBase(BaseModel):
    """Base AI chat message schema"""
    role: MessageRole
    content: str


class AIChatMessageCreate(AIChatMessageBase):
    """AI chat message creation schema"""
    pass


class AIChatMessageResponse(AIChatMessageBase):
    """AI chat message response schema"""
    id: int
    chatId: int
    createdAt: datetime

    class Config:
        from_attributes = True


class AIChatWithMessages(AIChatResponse):
    """AI chat with messages"""
    messages: list[AIChatMessageResponse] = []

    class Config:
        from_attributes = True
