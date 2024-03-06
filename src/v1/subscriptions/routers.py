from typing import Annotated

from fastapi import APIRouter, status, Depends, Path

from pydantic import UUID4
from src.dependencies import get_current_user, is_admin
from src.models import BaseResponseBody
from src.models import User
from src.v1.subscriptions.models import (
    SingleSubscriptionResponse,
    SubscriptionPayLinkCreate,
    SubscriptionStatusEnum
)
from src.v1.subscriptions.service import PostgresSubscriptionService
from src.v1.payment_providers.service import PaymentProviderService


router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "/get_pay_link",
    summary="Получить ссылку для оформления подписки",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Получить ссылку для оформления подписки",
)
async def get_pay_link(
    params: SubscriptionPayLinkCreate = Depends(),
    service: PaymentProviderService = PaymentProviderService,
) -> BaseResponseBody:
    pay_link = await service.generate_pay_link(params)
    return BaseResponseBody(data={"confirmation_url": pay_link})


@router.get(
    "/",
    summary="Получить подписку",
    response_model=SingleSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о подписке.",
)
async def get_subscription(
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    user: User = Depends(get_current_user),
) -> SingleSubscriptionResponse:
    subscription = await service.get_active_subscription(user_id=str(user.id))
    return SingleSubscriptionResponse(data=subscription)


@router.delete(
    "/",
    summary="Отменить подписку",
    response_model=SingleSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    description="Отменить подписку.",
)
async def cancel_subscription(
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    user: User = Depends(get_current_user),
) -> BaseResponseBody:
    subscription = await service.get_active_subscription(str(user.id))
    await service.delete(entity_id=subscription.id)
    return SingleSubscriptionResponse(data=subscription)
