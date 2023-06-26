from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import select
from app.models import Chat
from app.api import deps
from pydantic import BaseModel

router = APIRouter()


class ChatFormField(BaseModel):
    stmt_id: int
    seller_id: int
    history: str = ''


@router.post("/create")
async def chat(
        chat: ChatFormField,
        db: AsyncSession = Depends(deps.get_session),
):
    """add current chat"""
    db_chat = Chat(
        stmt_id=chat.stmt_id,
        seller_id=chat.seller_id,
        history=chat.history
    )
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    return db_chat


@router.get('/{chatId}')
async def get_chat(chatId: int, db: AsyncSession = Depends(deps.get_session), ):
    chat = (await db.scalars(select(Chat).where(Chat.id == chatId))).one()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No note with this id: {id} found")
    return chat
