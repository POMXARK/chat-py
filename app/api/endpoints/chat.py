from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import select
from app.models import Message
from app.api import deps
from pydantic import BaseModel

router = APIRouter()


class MessageFormField(BaseModel):
    text: str
    stmt: UUID
    from_: UUID
    to: UUID


@router.post("/post")
async def chat(
        message: MessageFormField,
        db: AsyncSession = Depends(deps.get_session),
):
    """add current chat"""
    _message = Message(
        text=message.text,
        stmt_id=message.stmt,
        from_user_id=message.from_,
        to_user_id=message.to
    )
    db.add(_message)
    try:
        await db.commit()
    except Exception as e:
        return e
    # await db.refresh(_message)
    return _message


@router.get('/load/{chatId}')
async def get_chat(chatId: int, db: AsyncSession = Depends(deps.get_session), ):
    chat = (await db.scalars(select(Message).where(Message.id == chatId))).one()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No note with this id: {id} found")
    return chat
