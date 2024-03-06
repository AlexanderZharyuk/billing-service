import logging
from typing import Annotated

from fastapi import APIRouter, status, Path

from src.v1.payment_providers.models import (
    SinglePaymentProviderResponse,
    SeveralPaymentProvidersResponse,
)
from src.v1.payment_providers.service import PaymentProviderService, PostgresPaymentProviderService

router = APIRouter(prefix="/payment_providers", tags=["Payment Providers"])
logger = logging.getLogger(__name__)


@router.get(
    "/{provider_id}",
    summary="Получить информацию о платеженом провайдере",
    response_model=SinglePaymentProviderResponse,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о платежном провайдере",
)
async def get_payment_provider(
    provider_id: Annotated[int, Path(examples=[1])],
    service: PostgresPaymentProviderService = PostgresPaymentProviderService
) -> SinglePaymentProviderResponse:
    payment_provider = await service.get(provider_id)
    return SinglePaymentProviderResponse(data=payment_provider)


@router.get(
    "/",
    summary="Получить список платежных провайдеров",
    response_model=SeveralPaymentProvidersResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список платежей",
    name="payments",
)
async def get_payments(
    service: PostgresPaymentProviderService = PostgresPaymentProviderService
) -> SeveralPaymentProvidersResponse:
    payment_providers = await service.get_all()
    return SeveralPaymentProvidersResponse(data=payment_providers)
