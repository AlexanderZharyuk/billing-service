from abc import ABC, abstractmethod


class BaseService(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def list(self, *args, **kwargs):
        pass

    @abstractmethod
    async def create(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def delete(self, *args, **kwargs):
        pass
