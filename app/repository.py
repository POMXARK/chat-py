from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from models import Message


class PostgresRepository:

    def __init__(self, db):
        self.db: AsyncSession = db


class MessageRepository(PostgresRepository):

    async def add_one(self, data, stmt_id):
        _message = Message(
            text=data['text'],
            stmt_id=stmt_id,
            user_id=data['user_id'],
            file_path=data['file_path']
        )
        self.db.add(_message)
        try:
            await self.db.commit()
        except Exception as e:
            return e

    async def find_messages_by_stmt(self, stmt_id):
        query = select(Message).where(Message.stmt_id == stmt_id)
        return (await self.db.scalars(query)).all()
