from fastapi import APIRouter, status

from src.models import BaseResponseBody
from src.v1.payment_providers.models import (
    PaymentProviderCreate,
    SinglePaymentProviderResponse,
    SeveralPaymentProvidersResponse,
    PaymentProviderUpdate
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


@router.get(
    "/",
    summary="Получить список платежных провайдеров",
    response_model=SeveralPaymentProvidersResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список платежей",
    name="payments",
)
async def get_payment_providers(
    service: PostgresPaymentProviderService = PostgresPaymentProviderService
) -> SeveralPaymentProvidersResponse:
    payment_providers = await service.get_all()
    return SeveralPaymentProvidersResponse(data=payment_providers)


@router.delete(
    "/{id}",
    summary="Удалить платежного провайдера",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Удалить платежного провайдера",
)
async def delete_payment_provider(
    payment_provider_id: int,
    service: PostgresPaymentProviderService = PostgresPaymentProviderService
) -> BaseResponseBody:
    await service.delete(payment_provider_id)
    return BaseResponseBody(data={"success": True})


@router.put(
    "/{id}",
    summary="Обновить платежного провайдера",
    response_model=SinglePaymentProviderResponse,
    status_code=status.HTTP_200_OK,
    description="Обновить план",
)
async def update_plan(
    payment_provider_id: int,
    data: PaymentProviderUpdate,
    service: PostgresPaymentProviderService = PostgresPaymentProviderService
) -> SinglePaymentProviderResponse:
    payment_provider = await service.update(entity_id=payment_provider_id, data=data)
    return SinglePaymentProviderResponse(data=payment_provider)
