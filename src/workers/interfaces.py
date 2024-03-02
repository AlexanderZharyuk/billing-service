from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from yookassa import Payment as yoPayment

from src.core.exceptions import InvalidParamsError
from src.core.interfaces import (BasePostgresService, TypeProvider,
                                 get_provider_from_user_choice)
from src.v1.features.models import Feature
from src.v1.payment_providers.models import PaymentProvider
from src.v1.payments.models import (Payment, PaymentMetadata,
                                    PaymentStatusEnum, PaymentUpdate)
from src.v1.plans.models import Plan
from src.v1.subscriptions.models import (Subscription, SubscriptionCreate,
                                         SubscriptionStatusEnum)
from src.workers.matching_successful_payments import logger


class BasePaymentMatchingWorker(BasePostgresService):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA):
        self._model = Payment
        self._session = session
        self.provider = get_provider_from_user_choice(type_provider)
        self.type_object = yoPayment
        self.date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.date_now = datetime.utcnow()

    async def get_payments_for_provider(self, params: dict) -> list[str]:
        payments = []
        try:
            logger.info("Uploading payments from a payment provider...")
            result = self.provider.get_all(type_object=self.type_object, params=params)
            async for res in result:
                for item in res:
                    payments.append(item.id)
            logger.info(f"Unloaded {len(payments)} payments from a payment provider")
            return payments
        except InvalidParamsError as error:
            logger.error(
                f"An error occurred when requesting payments from the provider: {error.detail['message']}"
            )

    async def get_payments_for_db(self, filter_: tuple) -> list[str]:
        try:
            logger.info("Uploading payments from a database...")
            result = await super().get_all(filter_=filter_)
            logger.info(f"Unloaded {len(result)} payments from a database.")
            result = [res.external_payment_id for res in result]
            return result
        except AttributeError as error:
            logger.info(f"An error occurred when requesting payments from the database:{error}")

    async def update_payment(self, entity_id: int, status: PaymentStatusEnum) -> Payment:
        payment = await super().update(entity_id=entity_id, data=PaymentUpdate(status=status))
        return payment

    async def create_subscription(self, metadata: PaymentMetadata, payment: Payment) -> BaseModel:
        self._model = Subscription
        subscription = SubscriptionCreate(
            user_id=metadata.user_id,
            status=SubscriptionStatusEnum.ACTIVE,
            started_at=self.date_now,
            ended_at=self.date_now + timedelta(days=31),
            plan_id=metadata.plan_id,
            payment_id=payment.id,
            payment_provider_id=metadata.payment_provider_id,
            currency=payment.currency,
            payment_method=payment.payment_method,
        )
        result = await super().create(
            entity=subscription
        )  # ToDo: update for method subscription service
        return result