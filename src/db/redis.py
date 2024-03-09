from src.db.storages import BaseCacheStorage


class RedisStorage(BaseCacheStorage):
    def __init__(self, client) -> None:
        self.client = client

    async def get(self, key: str) -> None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl_secs: int = None) -> list:
        return await self.client.set(key, value, ex=ttl_secs)

    async def close(self) -> None:
        await self.client.close()


cache_provider: RedisStorage | None = None


async def get_cache_provider():
    yield cache_provider
