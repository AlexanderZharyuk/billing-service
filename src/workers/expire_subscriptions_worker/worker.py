from datetime import datetime, time, timedelta

from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.interfaces import BasePostgresService, TypeProvider, get_provider_from_user_choice
from src.v1.features.models import Feature
from src.v1.payment_providers.models import PaymentProvider
from src.v1.payment_providers.service import get_payment_provider_service
from src.v1.payments.models import Payment, PaymentCreate, PaymentStatusEnum
from src.v1.payments.service import get_payment_service
from src.v1.plans.models import DurationUnitEnum, Plan, Price
from src.v1.plans.service import get_plan_service
from src.v1.subscriptions.models import Subscription, SubscriptionStatusEnum, SubscriptionUpdate
from src.v1.subscriptions.service import get_subscription_service
from src.workers.autopayment_worker import logger


class ExpireSubscriptionsWorker:
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA):
        self._session = session
        self.provider = get_provider_from_user_choice(type_provider)
        self.plan_service = get_plan_service(session=session)
        self.payment_provider_service = get_payment_provider_service(session=session)
        self.payment_service = get_payment_service(
            session=session,
            plan_service=self.plan_service,
            payment_provider_service=self.payment_provider_service,
        )
        self.subscription_service = get_subscription_service(
            session=session, payment_service=self.payment_service, plan_service=self.plan_service
        )
        self.date_now = datetime.combine(datetime.utcnow(), time.max)
        self.filter_date = self.date_now - timedelta(days=3)

    async def main(self) -> None:
        subscriptions = await self.get_subscriptions()
        if not subscriptions:
            logger.info("Expired subscriptions were not found.")
        for subscription in subscriptions:
            await self.update_subscription(
                entity_id=subscription.id,
                data=Subscription(
                    status=SubscriptionStatusEnum.EXPIRED, ended_at=subscription.ended_at
                ),
            )
            logger.info(
                f"Subscriptions with {subscription.id} has been updated with status EXPIRED."
            )
            return

    async def get_subscriptions(self) -> list[Subscription]:
        try:
            logger.info("Uploading subscriptions from a database...")
            filter_ = (
                Subscription.status == SubscriptionStatusEnum.ACTIVE,
                Subscription.ended_at <= self.filter_date,
            )
            subscriptions = await self.subscription_service.get_all(filter_=filter_)
            return subscriptions
        except AttributeError as error:
            logger.info(f"An error occurred when requesting payments from the database:{error}")

    async def update_subscription(
        self, entity_id: int, data: SubscriptionUpdate
    ) -> Subscription:
        result = await self.subscription_service.update(entity_id=entity_id, data=data)
        return result
