from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder
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

    return _message


@router.get('/load')
async def get_chat(stmt: UUID = None, from_: UUID = None, to: UUID = None, db: AsyncSession = Depends(deps.get_session)):
    query = select(Message)
    if stmt is not None:
        query = query.where(Message.stmt_id == stmt)
    if from_ is not None:
        query = query.where(Message.from_user_id == from_)
    if to is not None:
        query = query.where(Message.to_user_id == to)

    res = (await db.scalars(query)).all()
    test = jsonable_encoder(res[0])
    return res