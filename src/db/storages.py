from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncEngine


class DatabaseStorage(ABC):
    """Базовый класс объекта базы данных."""

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


class BaseCacheStorage(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def set(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        raise NotImplementedError
