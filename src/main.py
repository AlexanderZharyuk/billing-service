import logging

from contextlib import asynccontextmanager

import uvicorn

from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse

import src.constants as const
from src.core.config import LOGGING, settings
from src.db import postgres
from src.models import BaseExceptionBody
from src.v1.features.routers import router as features_router
from src.v1.healthcheck.routers import router as healthcheck_router
from src.v1.plans.routers import router as plan_router
from src.v1.admin import router as admin_router
from src.v1.subscriptions.routers import router as subscription_router
from src.v1.payments.routers import router as payment_router
from src.v1.webhooks.routers import router as webhooks_router


v1_router = APIRouter(
    prefix="/api/v1",
    responses={
        404: {"model": BaseExceptionBody},
        400: {"model": BaseExceptionBody},
    },
)

v1_router.include_router(healthcheck_router)
v1_router.include_router(features_router)
v1_router.include_router(plan_router)
v1_router.include_router(subscription_router)
v1_router.include_router(payment_router)
v1_router.include_router(webhooks_router)
v1_router.include_router(admin_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await postgres.db_provider.close()


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
