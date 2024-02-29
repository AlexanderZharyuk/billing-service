import uuid
from datetime import datetime, timedelta

from yookassa import Payment as yoPayment
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.interfaces import BasePostgresService, TypeProvider, get_provider_from_user_choice
from src.core.exceptions import InvalidParamsError
from src.v1.payments.models import Payment, PaymentMetadata, PaymentCreate, PaymentStatusEnum
from src.v1.plans.models import Plan
from src.v1.features.models import Feature
from src.v1.payment_providers.models import PaymentProvider
from src.v1.subscriptions.models import Subscription, SubscriptionCreate
from src.workers.matching_payments import logger


class MatchingSuccessPayments(BasePostgresService):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA):
        self._model = Payment
        self._session = session
        self.provider = get_provider_from_user_choice(type_provider)
        self.type_object = yoPayment
        self.payment_status = PaymentStatusEnum.SUCCEEDED.value
        self.date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.date_now = datetime.utcnow()

    async def matching_data(self) -> None:
        payments_for_provider = await self.get_payments_for_provider()
        payments_for_db = await self.get_payments_for_db()
        diff = set(payments_for_provider).difference(set(payments_for_db))
        if len(diff) == 0:
            logger.info("No discrepancies in payments were found.")
            return
        for item in diff:
            object_ = await self.provider.get(type_object=self.type_object, entity_id=item)
            payment_metadata = PaymentMetadata(**object_.metadata)
            payment = PaymentCreate(
                name=object_.description,
                subscription_id=payment_metadata.plan_id, #ToDo: correct after update model Payment
                payment_provider_id=payment_metadata.payment_provider_id,
                status=self.payment_status,
                currency=object_.amount.currency,
                amount=object_.amount.value,
                actual_payment_id=object_.id,
            )
            # ToDo: add method for create Subscripton after correct model Subscription
            create_payment = await super().create(payment)
            logger.info(f"A payment has been created with id {create_payment.id}.")

    async def get_payments_for_provider(self) -> list[str]:
        params = {
            "status": self.payment_status,
            "created_at.lt": self.date_now.strftime(self.date_format),
        }
        payments = []
        try:
            logger.info("Uploading payments from a payment provider...")
            result = self.provider.get_all(type_object=self.type_object, params=params)
            async for res in result:
                #todo:
                for item in res:
                    payments.append(item.id)
            logger.info(f"Unloaded {len(payments)} payments from a payment provider")
            return payments
        except InvalidParamsError as error:
            logger.error(
                f"An error occurred when requesting payments from the provider: {error.detail['message']}"
            )

    async def get_payments_for_db(self) -> list[str]:
        try:
            filter_ = (
                Payment.status == self.payment_status,
                Payment.created_at < self.date_now
            )
            logger.info("Uploading payments from a database...")
            result = await super().get_all(filter_=filter_)
            logger.info(f"Unloaded {len(result)} payments from a database.")
            result = [res.actual_payment_id for res in result]
            return result
        except AttributeError as error:
            logger.info(f"An error occurred when requesting payments from the database:{error}")
