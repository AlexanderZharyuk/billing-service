from typing import Annotated

from fastapi import APIRouter, Path, status

from src.v1.subscriptions.models import (
    SubscriptionPause, SingleSubscriptionResponse, SeveralSubscriptionsResponse
)
from src.v1.subscriptions.service import PostgresSubscriptionService


router = APIRouter(prefix="/subscriptions", tags=["Subscriptions Admin"])


@router.patch(
    "/{subscription_id}",
    summary="Приостановить подписку",
    response_model=SingleSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    description="Приостановить подписку.",
)
async def pause_subscription(
    subscription_id: Annotated[int, Path(examples=[1])],
    data: SubscriptionPause,
    service: PostgresSubscriptionService = PostgresSubscriptionService,
) -> SingleSubscriptionResponse:
    subscription = await service.pause(
        entity_id=subscription_id,
        data=data,
    )
    return SingleSubscriptionResponse(data=subscription)


@router.get(
    "/",
    summary="Получить подписки",
    response_model=SeveralSubscriptionsResponse,
    status_code=status.HTTP_200_OK,
    description="Получить подписки",
)
async def get_subscriptions(
    service: PostgresSubscriptionService = PostgresSubscriptionService,
) -> SeveralSubscriptionsResponse:
    subscriptions = await service.get_all()
    return SeveralSubscriptionsResponse(data=subscriptions)
