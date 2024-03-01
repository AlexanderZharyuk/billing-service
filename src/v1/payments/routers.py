from typing import Annotated

from fastapi import APIRouter, status, Depends, Path
from fastapi.responses import Response

from yookassa.domain.notification import WebhookNotification
from src.dependencies import get_current_user, is_admin
from src.models import User
from src.v1.payments.service import PostgresPaymentService
from src.v1.payments.models import (
    PaymentCreate,
    SinglePaymentResponse,
    SeveralPaymentsResponse,
)

router = APIRouter(prefix="/payments", tags=["Payments"])


# @router.post(
#     "/webhook",
#     summary="Подтверждение платежа.",
#     response_model=Response,
#     status_code=status.HTTP_200_OK,
#     description="Подтвердить платеж.",
# )
# async def approve_payment(
#         data: dict,
#         service: PostgresPaymentService = PostgresPaymentService
# ) -> Response:
#     # TODO:
#     # получить событие:
#     # payment.succeeded -> обновить статус платежа и создать подписку с активным статусом и правильными датами
#     # payment.waiting_for_capture -> ???
#     # payment.canceled -> обновить статус платежа
#     # refund.succeeded -> обновить статус подписки
#     #
#
#     notification_object = WebhookNotification(data)
#     event = notification_object.event
#
#     payment = notification_object.object
#     payment = await service.update(data)
#
#     return Response(status_code=200)


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
    current_user: User = Depends(get_current_user),
) -> SinglePaymentResponse:
    if is_admin(current_user):
        payment = await service.get(payment_id)
    else:
        payment = await service.get_one_by_filter(
            filter_={"id": payment_id, "user_id": current_user.id}
        )
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
    service: PostgresPaymentService = PostgresPaymentService,
    current_user: User = Depends(get_current_user),
) -> SeveralPaymentsResponse:
    if is_admin(current_user):
        payments = await service.get_all()
    else:
        payments = await service.get_all(filter_={"user_id": current_user.id})
    return SeveralPaymentsResponse(data=payments)
