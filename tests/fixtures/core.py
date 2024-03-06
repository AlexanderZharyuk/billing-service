import asyncio
from sqlalchemy.pool import NullPool
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.core.config import settings
from src.db.postgres import db_provider
from src.main import app
from src.models import Base
from tests.utils.testing_data import test_data

from src.v1.plans.models import Plan
from src.v1.subscriptions.models import Subscription
from src.v1.payments.models import Payment

data_mapping = {
    "plans": Plan,
    # "subscriptions": Subscription,
    # "payments": Payment
}


pg_connect_string = (
    f"postgresql+asyncpg://{settings.postgres_user}:"
    f"{settings.postgres_password}@{settings.postgres_host}:"
    f"{settings.postgres_port}/"
)


async def create_database():
    pg_dsn = f"{pg_connect_string}postgres"
    engine = create_async_engine(pg_dsn, future=True).execution_options(
        isolation_level="AUTOCOMMIT"
    )
    async with engine.connect() as c:
        async with c.begin():
            await c.execute(text(f"CREATE DATABASE {settings.postgres_db}_test_db;"))
    await engine.dispose()


async def delete_database():
    pg_dsn = f"{pg_connect_string}postgres"
    engine = create_async_engine(pg_dsn, future=True).execution_options(
        isolation_level="AUTOCOMMIT"
    )
    async with engine.connect() as c:
        async with c.begin():
            await c.execute(text(f"DROP DATABASE IF EXISTS {settings.postgres_db}_test_db;"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    pg_dsn = f"{pg_connect_string}{settings.postgres_db}_test_db"
    await delete_database()
    await create_database()
    engine = create_async_engine(pg_dsn, future=True, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield conn
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db(db_engine):
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def insert_data(db: AsyncSession):
    for table, model in data_mapping.items():
        for row in test_data[table]:
            db.add(model(**row))
    await db.commit()
    result = await db.execute(text(f"SELECT * FROM plans"))
    print(result.fetchall())


@pytest_asyncio.fixture(scope="session")
async def http_client(db: AsyncSession):
    app.dependency_overrides[db_provider] = lambda: db
    client = AsyncClient(
        app=app,
        base_url="http://api_test"
    )
    yield client
    await client.aclose()