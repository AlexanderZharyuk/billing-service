import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from yookassa.domain.notification import WebhookNotification

from src.v1.payments.models import (
    PaymentUpdate,
)
from src.v1.subscriptions.models import SubscriptionCreate, SubscriptionStatusEnum
from src.v1.subscriptions.service import PostgresSubscriptionService
from src.v1.payments.service import PostgresPaymentService
from src.v1.payments.models import PaymentMetadata

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


@router.post(
    "/yookassa",
    summary="Получить информацию о статусе платежа YooKassa.",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о статусе платежа YooKassa.",
)
async def status_payment_yookassa(
    data: dict,
    payment_service: PostgresPaymentService = PostgresPaymentService,
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

    # TODO: Добавить логгинг. Провести рефактор
    match event:
        case "payment.succeeded" | "payment.canceled":
            payment_update = PaymentUpdate(
                status=notification_object.object.status,
                payment_method=notification_object.object.payment_method.type
            )
            payment = await payment_service.update(
                external_payment_id=notification_object.object.id, data=payment_update
            )
            if event == "payment.succeeded":
                payment_metadata = PaymentMetadata(**notification_object.object.metadata)
                subscription = SubscriptionCreate(
                    user_id=payment_metadata.user_id,
                    status=SubscriptionStatusEnum.ACTIVE,
                    plan_id=payment_metadata.plan_id,
                    payment_id=payment.id
                )
                await subscription_service.create(subscription)
        case "payment.waiting_for_capture":
            ...
        case "refund.succeeded":
            ...

    return JSONResponse(status_code=200, content={"received": True})
