import asyncio
import asyncpg
import pytest
from httpx import AsyncClient
from src.core.config import settings
from tests.utils.data import test_data


@pytest.fixture
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def http_client():
    client = AsyncClient()
    yield client
    await client.aclose()


@pytest.fixture
async def pg_conn():

    conn = await asyncpg.connect(
        f"postgresql://{settings.postgres_user}:"
        f"{settings.postgres_password}@{settings.postgres_host}:"
        f"{settings.postgres_port}/{settings.postgres_db}"
    )
    yield conn

    await conn.close()
