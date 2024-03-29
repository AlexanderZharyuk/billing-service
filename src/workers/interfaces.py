import logging

from datetime import datetime

from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from yookassa import Payment as yoPayment

from src.core.exceptions import InvalidParamsError
from src.core.interfaces.database import BasePostgresService
from src.core.helpers import rollback_transaction
from src.v1.features.models import Feature
from src.v1.payment_providers.models import PaymentProvider
from src.v1.payment_providers.service import TypeProvider, AbstractProviderMixin, get_payment_provider_service
from src.v1.payments.models import Payment, PaymentMetadata, PaymentStatusEnum, PaymentUpdate
from src.v1.payments.service import get_payment_service
from src.v1.plans.models import Plan
from src.v1.plans.service import get_plan_service
from src.v1.prices.models import Price
from src.v1.refunds.models import Refund, RefundReason
from src.v1.subscriptions.models import Subscription, SubscriptionCreate, SubscriptionStatusEnum
from src.v1.subscriptions.service import get_subscription_service
from src.db.redis import get_cache_provider

logger = logging.getLogger(__name__)


class BasePaymentMatchingWorker(BasePostgresService):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA.value):
        self._model = Payment
        self._session = session
        get_provider = AbstractProviderMixin.get_provider(provider_name=type_provider)
        self.payment_provider_service = get_payment_provider_service(session=session)
        self.plan_service = get_plan_service(session=session)
        self.payment_service = get_payment_service(
            session=session,
            plan_service=self.plan_service,
        )
        self.subscriptions_service = get_subscription_service(
            session=session,
            payment_service=self.payment_provider_service,
            plan_service=self.plan_service,
        )
        self.cache_provider = get_cache_provider()
        self.provider = get_provider(self.payment_service, self.plan_service, self.cache_provider)
        self.type_object = yoPayment
        self.date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.date_now = datetime.utcnow()

    async def get_payments_for_provider(self, params: dict) -> list[str]:
        payments = []
        try:
            logger.info("Uploading payments from a payment provider...")
            result = await self.provider.get_all(type_object=self.type_object, params=params)
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

    async def update_payment(self, entity_id: int, data: PaymentUpdate, commit: bool = True) -> Payment:
        payment = await super().update(
            entity_id=entity_id, data=data, commit=commit
        )
        return payment

    async def create_subscription(self, metadata: PaymentMetadata, commit: bool = True) -> BaseModel:
        subscription = SubscriptionCreate(
            user_id=metadata.user_id,
            status=SubscriptionStatusEnum.ACTIVE,
            started_at=self.date_now,
            plan_id=metadata.plan_id
        )
        result = await self.subscriptions_service.create(entity=subscription, commit=commit)
        return result

    @rollback_transaction(method="CREATE OR UPDATE")
    async def session_commit(self) -> None:
        await self.session.commit()
        return
