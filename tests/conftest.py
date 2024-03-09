import asyncio
import asyncpg
import pytest

pytest_plugins = (
    "tests.fixtures.core",
    "tests.fixtures.workers"
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

