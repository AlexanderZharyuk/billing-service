from fastapi import APIRouter, status

from src.v1.payment_providers.models import (
    PaymentProviderCreate, SinglePaymentProviderResponse
)
from src.v1.payment_providers.service import PostgresPaymentProviderService


router = APIRouter(prefix="/payment_providers", tags=["Payment Providers Admin"])


@router.post(
    "/",
    summary="Создать нового платежного провайдера",
    response_model=SinglePaymentProviderResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать нового платежного провайдера",
)
async def create_payment_provider(
    data: PaymentProviderCreate,
    service: PostgresPaymentProviderService = PostgresPaymentProviderService,
) -> SinglePaymentProviderResponse:
    subscription = await service.create(data)
    return SinglePaymentProviderResponse(data=subscription)
