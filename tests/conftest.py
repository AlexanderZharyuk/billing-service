import asyncio

import pytest
from httpx import AsyncClient


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

