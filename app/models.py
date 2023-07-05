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

from sqlalchemy import String, TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.postgresql import UUID, INTEGER, TEXT
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


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[[int]] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    created_at: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True),
                                                    nullable=False, server_default=text('now()'))
    updated_at: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True),
                                                    nullable=False, server_default=text('now()'))
    text: Mapped[[str]] = mapped_column(TEXT)
    from_user_id: Mapped[[str]] = mapped_column(UUID)
    to_user_id: Mapped[[str]] = mapped_column(UUID)
    stmt_id: Mapped[[str]] = mapped_column(UUID)
    read_at: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    read_by: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
