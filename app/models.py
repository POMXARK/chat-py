"""
SQL Alchemy models declaration.
https://docs.sqlalchemy.org/en/14/orm/declarative_styles.html#example-two-dataclasses-with-declarative-table
Dataclass style for powerful autocompletion support.

https://alembic.sqlalchemy.org/en/latest/tutorial.html
Note, it is used by alembic migrations logic, see `alembic/env.py`

Alembic shortcuts:
# create migration
alembic revision --autogenerate -m "migration_name"

# apply all migrations
alembic upgrade head
"""
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID, JSON, INTEGER, BOOLEAN
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_model"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(254), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[[int]] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    stmt_id: Mapped[[int]] = mapped_column(INTEGER)
    seller_id: Mapped[[int]] = mapped_column(INTEGER)
    history: Mapped[[str]] = mapped_column(JSON)
    is_active: Mapped[[bool]] = mapped_column(BOOLEAN, default=True)