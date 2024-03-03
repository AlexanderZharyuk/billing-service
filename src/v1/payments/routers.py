import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends, Path
from fastapi.responses import JSONResponse

from yookassa.domain.notification import WebhookNotification
from src.dependencies import get_current_user, is_admin
from src.models import User
from src.v1.payments.service import PostgresPaymentService
from src.v1.payments.models import (
    PaymentUpdate,
    SinglePaymentResponse,
    SeveralPaymentsResponse,
)
from src.v1.subscriptions.service import PostgresSubscriptionService

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)


@router.post(
    "/webhook",
    summary="Получить информацию о статусе платежа.",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о статусе платежа.",
)
async def approve_payment(
    data: dict,
    service: PostgresPaymentService = PostgresPaymentService,
    subscription_service: PostgresSubscriptionService = PostgresSubscriptionService,
) -> JSONResponse:
    """
    # payment.succeeded -> обновить статус платежа и создать подписку с активным статусом и правильными датами
    # payment.waiting_for_capture -> ???
    # payment.canceled -> обновить статус платежа
    # refund.succeeded -> обновить статус подписки?

    {'type': 'notification',
    'event': 'payment.succeeded',
    'object': {'id': '2d76b47a-000f-5000-a000-16bb63f881fc',
                'status': 'succeeded',
                'amount': {'value': '1000.00', 'currency': 'RUB'},
                'income_amount': {'value': '965.00', 'currency': 'RUB'},
                'recipient': {'account_id': '341451', 'gateway_id': '2192359'},
                'payment_method': {'type': 'bank_card', 'id': '2d76b47a-000f-5000-a000-16bb63f881fc',
                                    'saved': True, 'title': 'Bank card *4444',
                                    'card': {'first6': '555555', 'last4': '4444', 'expiry_year': '2025',
                                            'expiry_month': '05', 'card_type': 'MasterCard', 'issuer_country': 'US'}},
                'captured_at': '2024-03-03T16:10:58.476Z',
                'created_at': '2024-03-03T16:09:30.162Z',
                'test': True,
                'refunded_amount': {'value': '0.00', 'currency': 'RUB'},
                'paid': True,
                'refundable': True,
                'metadata': {'payment_provider_id': '1',
                            'user_id': '3f8cd1fb-0cc0-4e99-ba39-9478fa007731', 'plan_id': '1'},
                'authorization_details': {'rrn': '296939313996726', 'auth_code': '494558',
                'three_d_secure': {'applied': False, 'method_completed': False, 'challenge_completed': False}}}}

    """
    notification_object = WebhookNotification(data)
    event = notification_object.event

    match event:
        case "payment.succeeded":
            payment_update = PaymentUpdate(status=notification_object.object.status)
            await service.update(
                external_payment_id=notification_object.object.id, data=payment_update
            )
            await subscription_service.create_webhook(
                external_payment_id=notification_object.object.id,
                user_id=notification_object.object.metadata["user_id"],
                plan_id=notification_object.object.metadata["plan_id"],
            )
        case "payment.waiting_for_capture":
            ...
        case "payment.canceled":
            payment_update = PaymentUpdate(status=notification_object.object.status)
            await service.update(
                external_payment_id=notification_object.object.id, data=payment_update
            )
        case "refund.succeeded":
            ...

    return JSONResponse(status_code=200, content={"received": True})


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
