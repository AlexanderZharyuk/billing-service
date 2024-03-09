import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends, Path

from src.dependencies import get_current_user
from src.models import User
from src.v1.payments.models import (
    SinglePaymentResponse,
    SeveralPaymentsResponse,
)
from src.v1.payments.service import PostgresPaymentService
from src.v1.subscriptions.service import PostgresSubscriptionService
from src.core.exceptions import EntityNotFoundError

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)


@router.get(
    "/{payment_id}",
    summary="Получить информацию о платеже",
    response_model=SinglePaymentResponse,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о платеже",
)
async def get_payment(
    payment_id: Annotated[int, Path(examples=[1])],
    service: PostgresPaymentService = PostgresPaymentService,
    user: User = Depends(get_current_user),
) -> SinglePaymentResponse:
    payment = await service.get(payment_id)
    if not payment.subscription:
        raise EntityNotFoundError
    if payment.subscription.user_id != str(user.id):
        raise EntityNotFoundError
    return SinglePaymentResponse(data=payment)


@router.get(
    "/",
    summary="Получить список платежей",
    response_model=SeveralPaymentsResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список платежей",
    name="payments",
)
async def get_payments(
    service: PostgresSubscriptionService = PostgresSubscriptionService,
    user: User = Depends(get_current_user),
) -> SeveralPaymentsResponse:
    subscriptions = await service.get_all(filter_={"user_id": str(user.id)})
    payments = []
    for subscription in subscriptions:
        payments.extend(subscription.payments)
    return SeveralPaymentsResponse(data=payments)
