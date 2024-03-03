from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from yookassa import Payment as yoPayment

from src.core.interfaces import BasePostgresService, TypeProvider, get_provider_from_user_choice
from src.v1.features.models import Feature
from src.v1.payment_providers.models import PaymentProvider
from src.v1.payment_providers.service import get_payment_provider_service
from src.v1.payments.models import Payment, PaymentCreate, PaymentMetadata, PaymentStatusEnum
from src.v1.payments.service import get_payment_service
from src.v1.plans.models import DurationUnitEnum, Plan, Price
from src.v1.plans.service import get_plan_service
from src.v1.subscriptions.models import Subscription, SubscriptionStatusEnum, SubscriptionUpdate
from src.workers.autopayment_worker import logger


class AutopaymentsWorker(BasePostgresService):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA):
        self._model = Payment
        self._session = session
        self.provider = get_provider_from_user_choice(type_provider)
        self.plan_service = get_plan_service(session=session)
        self.payment_provider_service = get_payment_provider_service(session=session)
        self.payment_service = get_payment_service(
            session=session,
            plan_service=self.plan_service,
            payment_provider_service=self.payment_provider_service,
        )
        self.type_object = yoPayment
        self.date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.date_now = datetime.combine(datetime.utcnow(), time.max)

    async def autopayments(self):
        subscriptions = await self.get_subscriptions()
        if len(subscriptions) == 0:
            logger.info("No subscriptions in need of auto-renewal were found.")
        for item in subscriptions:
            await self.update_subscription(
                entity_id=item.id, data=SubscriptionUpdate(status=SubscriptionStatusEnum.EXPIRED)
            )
            payment = await self.get_payment(entity_id=item.payment_id)
            external_payment_id = payment.external_payment_id
            price = await self.get_price(item.plan_id)
            plan = await self.plan_service.get(entity_id=item.plan_id)
            external_payment = await self.create_external_payment(
                payment_method_id=external_payment_id, price=price
            )
            if external_payment.status == PaymentStatusEnum.CANCELED:
                logger.info(f"Autopayment for a subscription with {item.id} failed.")
                return
            ended_at = await self.calculationg_end_date(plan=plan)
            self._model = Payment
            payment_create = await super().create(
                entity=PaymentCreate(
                    payment_provider_id=payment.payment_provider_id,
                    payment_method=payment.payment_method,
                    status=PaymentStatusEnum.SUCCEEDED,
                    currency=external_payment.amount.currency,
                    amount=external_payment.amount.value,
                    external_payment_id=external_payment_id,
                )
            )
            logger.info(f"A payment has been created with id {payment_create.id}.")
            await self.update_subscription(
                entity_id=item.id,
                data=Subscription(status=SubscriptionStatusEnum.ACTIVE, ended_at=ended_at),
            )

    async def get_subscriptions(self) -> list:
        self._model = Subscription
        try:
            logger.info("Uploading subscriptions from a database...")
            filter_ = (Subscription.ended_at <= self.date_now,)
            subscriptions = await super().get_all(filter_=filter_)
            logger.info(f"Unloaded {len(subscriptions)} subscriptions from a database")
            return subscriptions
        except AttributeError as error:
            logger.info(f"An error occurred when requesting payments from the database:{error}")

    async def get_payment(self, entity_id: int) -> Payment:
        self._model = Payment
        result = await super().get(entity_id=entity_id)
        return result

    async def get_price(self, plan_id: int) -> Price:
        self._model = Price
        result = await super().get_one_by_filter(filter_={"plan_id": plan_id})
        return result

    async def update_subscription(self, entity_id: int, data: SubscriptionUpdate) -> Subscription:
        self._model = Subscription
        result = await super().update(entity_id=entity_id, data=data)
        logger.info(f"Subscriptions with {entity_id} has been updated.")
        return result

    async def create_external_payment(self, payment_method_id: str, price: Price) -> dict:
        result = await self.provider.create(
            type_object=self.type_object,
            params={
                "amount": {
                    "value": price.amount,
                    "currency": price.currency.value,
                },
                "capture": True,
                "payment_method_id": payment_method_id,
                "description": "Auto-renewal of subscription",
            },
        )
        return result

    async def calculationg_end_date(self, plan: Plan) -> datetime:
        duration = plan.duration
        duration_unit = plan.duration_unit
        match duration_unit:
            case DurationUnitEnum.MONTH:
                return self.date_now + relativedelta(months=+duration)
            case DurationUnitEnum.YEAR:
                return self.date_now + relativedelta(years=+duration)
