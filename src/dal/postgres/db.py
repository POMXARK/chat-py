from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from dal.postgres import config
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

sqlalchemy_database_uri = config.settings.DEFAULT_SQLALCHEMY_DATABASE_URI
async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session