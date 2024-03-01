from typing import Annotated

from fastapi import APIRouter, status, Depends, Request, Path
from fastapi.responses import RedirectResponse

from src.dependencies import get_current_user, is_admin
from src.models import BaseResponseBody
from src.models import User
from src.v1.subscriptions.models import (
    SubscriptionCreate,
    SingleSubscriptionResponse,
    SeveralSubscriptionsResponse,
    SubscriptionPause,
)
from src.v1.subscriptions.service import PostgresSubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "/{subscription_id}",
    summary="Получить подписку",
    response_model=SingleSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о подписке.",
)
async def get_subscription(
    subscription_id: Annotated[int, Path(examples=[1])],
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    current_user: User = Depends(get_current_user),
) -> SingleSubscriptionResponse:
    if is_admin(current_user):
        subscription = await service.get(subscription_id)
    else:
        subscription = await service.get_one_by_filter(
            filter_={"id": subscription_id, "user_id": current_user.id}
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
    current_user: User = Depends(get_current_user),
) -> SeveralSubscriptionsResponse:
    if is_admin(current_user):
        subscriptions = await service.get_all()
    else:
        subscriptions = await service.get_all(filter_={"user_id": current_user.id})
    return SeveralSubscriptionsResponse(data=subscriptions)


@router.post(
    "/",
    summary="Создать подписку",
    response_model=BaseResponseBody,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    description="Создать подписку.",
)
async def create_subscription(
    data: SubscriptionCreate,
    request: Request,
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    current_user: User = Depends(get_current_user),
) -> BaseResponseBody:
    if data.return_url is None:
        data.return_url = request.url_for("payments")
    redirect_url = await service.create(entity=data, user=current_user)
    return BaseResponseBody(data={"redirect_url": redirect_url})


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
    current_user: User = Depends(get_current_user),
) -> SingleSubscriptionResponse:
    subscription = await service.update(
        entity_id=subscription_id,
        data=data,
        user=current_user if not is_admin(current_user) else None,
    )
    return SingleSubscriptionResponse(data=subscription)


@router.delete(
    "/{subscription_id}",
    summary="Отменить подписку",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Отменить подписку.",
)
async def cancel_subscription(
    subscription_id: Annotated[int, Path(examples=[1])],
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    current_user: User = Depends(get_current_user),
) -> BaseResponseBody:
    subscription = await service.update(
        entity_id=subscription_id,
        user=current_user if not is_admin(current_user) else None,
    )
    return SingleSubscriptionResponse(data=subscription)
