import asyncio
from sqlalchemy.pool import NullPool
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.core.config import settings
from src.db.postgres import db_provider, AsyncPostgresDatabaseProvider
from src.main import app
from src.models import Base
from tests.utils.testing_data import test_data

from src.v1.plans.models import Plan
from src.v1.features.models import Feature
from src.v1.subscriptions.models import Subscription
from src.v1.payments.models import Payment
from src.v1.payment_providers.models import PaymentProvider
from src.v1.refunds.models import Refund, RefundReason

session = AsyncPostgresDatabaseProvider()

data_mapping = {
    "features": Feature,
    "plans": Plan,
    "payment_providers": PaymentProvider,
    "subscriptions": Subscription,
    "payments": Payment,
    "refund_reasons": RefundReason,
    "refunds": Refund,
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
    engine = create_async_engine(pg_dsn, future=True)
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
            obj = model(**row)
            db.add(obj)
    await db.commit()

    # result = await db.execute(text(f"SELECT * FROM plans"))
    # print(result.fetchall())


@pytest_asyncio.fixture
async def http_client(db: AsyncSession, insert_data):
    app.dependency_overrides[db_provider] = lambda: db
    client = AsyncClient(
        app=app,
        base_url="http://api_test"
    )
    yield client
    await client.aclose()
