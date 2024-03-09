from typing import Annotated
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.storages import DatabaseStorage


class AsyncPostgresDatabaseProvider(DatabaseStorage):
    """Класс БД PostgreSQL"""

    def __init__(self):
        super().__init__(
            engine=create_async_engine(settings.pg_dsn, future=True, echo=settings.debug)
        )

    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(self.engine, expire_on_commit=False) as session:
            yield session

    async def close(self) -> None:
        await self.engine.dispose()


db_provider = AsyncPostgresDatabaseProvider()
DatabaseSession = Annotated[AsyncSession, Depends(db_provider)]
