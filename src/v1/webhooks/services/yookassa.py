from datetime import datetime

from yookassa.domain.notification.webhook_notification import WebhookNotification, RefundWebhookNotification

from src.v1.payments.models import PaymentMetadata, PaymentUpdate, Payment, PaymentStatusEnum
from src.v1.payments.service import PaymentService, PostgresPaymentService
from src.v1.subscriptions.models import (
    Subscription,
    SubscriptionCreate,
    SubscriptionStatusEnum,
    SubscriptionUpdate
)
from src.v1.subscriptions.service import PostgresSubscriptionService


class YooKassaWebhookService:

    def __init__(
        self,
        payment_service: PaymentService,
        subscription_service: PostgresSubscriptionService
    ):
        self.payment_service = payment_service
        self.subscription_service = subscription_service

    async def activate_subscription(self, notification_data: WebhookNotification):
        payment_metadata = PaymentMetadata(**notification_data.object.metadata)
        subscription = await self.subscription_service.get_one_by_filter(
            {"user_id": str(payment_metadata.user_id), "status": SubscriptionStatusEnum.ACTIVE}
        )
        if subscription:
            new_end_date = datetime.utcnow() + Subscription.get_end_time_delta(subscription.plan)
            subscription_data = SubscriptionUpdate(
                status=SubscriptionStatusEnum.ACTIVE,
                ended_at=new_end_date
            )
            await self.subscription_service.update(subscription.id, subscription_data)
        else:
            subscription_data = SubscriptionCreate(
                user_id=str(payment_metadata.user_id),
                status=SubscriptionStatusEnum.ACTIVE,
                plan_id=payment_metadata.plan_id,
            )
            subscription = await self.subscription_service.create(subscription_data)

        payment_update_data = PaymentUpdate(
            status=PaymentStatusEnum.SUCCEEDED,
            payment_method=notification_data.object.payment_method.type,
            subscription_id=subscription.id
        )
        await self.payment_service.update(
            notification_data.object.payment_method.id, payment_update_data
        )

    async def disable_subscription(self, notification_data: RefundWebhookNotification):
        payment = await self.payment_service.get_one_by_filter(
            {"external_payment_id": notification_data.object.payment_id}
        )
        subscription_data = SubscriptionUpdate(
            status=SubscriptionStatusEnum.DELETED,
            ended_at=datetime.utcnow()
        )
        await self.subscription_service.update(payment.subscription_id, subscription_data)
        payment_update_data = PaymentUpdate(status=PaymentStatusEnum.REFUNDED)
        await self.payment_service.update(notification_data.object.payment_id, payment_update_data)


def get_yookassa_webhook_service(
    payment_service: PostgresPaymentService = PostgresPaymentService,
    subscription_service: PostgresSubscriptionService = PostgresSubscriptionService
) -> YooKassaWebhookService:
    return YooKassaWebhookService(payment_service, subscription_service)
