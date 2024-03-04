from typing import Annotated

from fastapi import APIRouter, status, Depends, Path

from pydantic import UUID4
from src.dependencies import get_current_user, is_admin
from src.models import BaseResponseBody
from src.models import User
from src.v1.subscriptions.models import (
    SingleSubscriptionResponse,
    SubscriptionPayLinkCreate
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
    "/{user_id}/{subscription_id}",
    summary="Получить подписку",
    response_model=SingleSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о подписке.",
)
async def get_subscription(
    user_id: str | int | UUID4,
    subscription_id: Annotated[int, Path(examples=[1])],
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    user: User = Depends(get_current_user),
) -> SingleSubscriptionResponse:
    subscription = await service.get_one_by_filter(
        filter_={"id": subscription_id, "user_id": user.id}, dump_to_model=False
    )
    return SingleSubscriptionResponse(data=subscription)


@router.delete(
    "{user_id}/{subscription_id}",
    summary="Отменить подписку",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Отменить подписку.",
)
async def cancel_subscription(
    user_id: str | int | UUID4,
    subscription_id: Annotated[int, Path(examples=[1])],
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    current_user: User = Depends(get_current_user),
) -> BaseResponseBody:
    subscription = await service.delete(
        entity_id=subscription_id,
    )
    return SingleSubscriptionResponse(data=subscription)
