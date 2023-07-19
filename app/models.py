from sqlalchemy import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.postgresql import UUID, INTEGER, TEXT, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[[int]] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    created_at: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True),
                                                    nullable=False, server_default=text('now()'))
    updated_at: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True),
                                                    nullable=False, server_default=text('now()'))
    text: Mapped[[str]] = mapped_column(TEXT)
    user_id: Mapped[[str]] = mapped_column(UUID)
    stmt_id: Mapped[[str]] = mapped_column(UUID)
    read_at: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    read_by: Mapped[[TIMESTAMP]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    file_path: Mapped[[JSON]] = mapped_column(JSON, nullable=True)
