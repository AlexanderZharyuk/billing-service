import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import create_async_engine

import src.constants as const
from src.core.config import LOGGING, settings
from src.db import postgres
from src.models import BaseExceptionBody, Base
from src.v1.features.routers import router as features_router
from src.v1.healthcheck.routers import router as healthcheck_router
from sqlmodel import SQLModel

v1_router = APIRouter(
    prefix="/api/v1",
    responses={
        404: {"model": BaseExceptionBody},
        400: {"model": BaseExceptionBody},
    },
)

v1_router.include_router(healthcheck_router)
v1_router.include_router(features_router)


async def create_tables():
    from src.v1.features.models import Feature
    from src.v1.payment_providers.models import PaymentProvider
    from src.v1.plans.models import Plan, PlansToFeaturesLink
    from src.v1.subscriptions.models import Subscription
    from src.v1.invoices.models import Invoice
    from src.v1.payments.models import Payment

    engine = create_async_engine(
        settings.pg_dsn,
        echo=True,
        future=True,
        pool_size=20,
        max_overflow=20,
        pool_recycle=3600,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def drop_tables():
    from src.v1.features.models import Feature
    from src.v1.payment_providers.models import PaymentProvider
    from src.v1.plans.models import Plan, PlansToFeaturesLink
    from src.v1.subscriptions.models import Subscription
    from src.v1.invoices.models import Invoice
    from src.v1.payments.models import Payment

    engine = create_async_engine(
        settings.pg_dsn,
        echo=True,
        future=True,
        pool_size=20,
        max_overflow=20,
        pool_recycle=3600,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await drop_tables()
    await create_tables()
    # run
    yield
    # shutdown
    await postgres.db_session.close()


app = FastAPI(
    title=const.APP_API_DOCS_TITLE,
    version=const.APP_VERSION,
    description=const.APP_DESCRIPTION,
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/docs.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(v1_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.listen_addr,
        port=settings.listen_port,
        log_config=LOGGING,
        log_level=logging.INFO,
    )
