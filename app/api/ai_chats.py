from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from prisma.models import User
from app.core.deps import get_db, get_current_user
from app.schemas.ai_chat import (
    AIChatCreate,
    AIChatUpdate,
    AIChatResponse,
    AIChatMessageCreate,
    AIChatMessageResponse,
    AIChatWithMessages
)

router = APIRouter(prefix="/ai-chats", tags=["AI Chats"])


@router.post("/", response_model=AIChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: AIChatCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Create a new AI chat"""
    chat = await db.aichat.create(
        data={
            "userId": current_user.id,
            "title": chat_data.title,
        }
    )

    return chat


@router.get("/", response_model=list[AIChatResponse])
async def get_my_chats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)],
    skip: int = 0,
    limit: int = 50
):
    """Get current user's AI chats"""
    chats = await db.aichat.find_many(
        where={"userId": current_user.id},
        skip=skip,
        take=limit,
        order={"updatedAt": "desc"}
    )

    return chats


@router.get("/{chat_id}", response_model=AIChatWithMessages)
async def get_chat_by_id(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get AI chat by ID with messages"""
    chat = await db.aichat.find_unique(
        where={"id": chat_id},
        include={"messages": {"order_by": {"createdAt": "asc"}}}
    )

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    # Check if user owns this chat
    if chat.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this chat"
        )

    return chat


@router.put("/{chat_id}", response_model=AIChatResponse)
async def update_chat(
    chat_id: int,
    chat_update: AIChatUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Update AI chat"""
    chat = await db.aichat.find_unique(where={"id": chat_id})

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    # Check if user owns this chat
    if chat.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this chat"
        )

    update_data = chat_update.model_dump(exclude_unset=True)
    updated_chat = await db.aichat.update(
        where={"id": chat_id},
        data=update_data
    )

    return updated_chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Delete AI chat"""
    chat = await db.aichat.find_unique(where={"id": chat_id})

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    # Check if user owns this chat
    if chat.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this chat"
        )

    await db.aichat.delete(where={"id": chat_id})

    return None


@router.post("/{chat_id}/messages", response_model=AIChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message_to_chat(
    chat_id: int,
    message_data: AIChatMessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Add a message to AI chat"""
    # Check if chat exists and user owns it
    chat = await db.aichat.find_unique(where={"id": chat_id})

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    if chat.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add messages to this chat"
        )

    # Create message
    message = await db.aichatmessage.create(
        data={
            "chatId": chat_id,
            "role": message_data.role,
            "content": message_data.content,
        }
    )

    # Update chat's updatedAt
    await db.aichat.update(
        where={"id": chat_id},
        data={"updatedAt": message.createdAt}
    )

    return message


@router.get("/{chat_id}/messages", response_model=list[AIChatMessageResponse])
async def get_chat_messages(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Prisma, Depends(get_db)]
):
    """Get all messages in a chat"""
    # Check if chat exists and user owns it
    chat = await db.aichat.find_unique(where={"id": chat_id})

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    if chat.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view messages in this chat"
        )

    messages = await db.aichatmessage.find_many(
        where={"chatId": chat_id},
        order={"createdAt": "asc"}
    )

    return messages
