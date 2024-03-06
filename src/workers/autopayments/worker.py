from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from yookassa import Payment as yoPayment
from yookassa.domain.response import PaymentResponse

from src.core.exceptions import InvalidParamsError
from src.core.helpers import rollback_transaction
from src.core.interfaces import BasePostgresService, TypeProvider, get_provider_from_user_choice
from src.v1.features.models import Feature
from src.v1.payment_providers.models import PaymentProvider
from src.v1.payment_providers.service import get_payment_provider_service
from src.v1.payments.models import Payment, PaymentCreate, PaymentStatusEnum
from src.v1.payments.service import get_payment_service
from src.v1.plans.models import DurationUnitEnum, Plan
from src.v1.plans.service import get_plan_service
from src.v1.prices.models import Price
from src.v1.prices.service import get_price_service
from src.v1.subscriptions.models import Subscription, SubscriptionStatusEnum, SubscriptionUpdate
from src.v1.subscriptions.service import get_subscription_service
from src.workers.autopayments import logger


class AutopaymentsWorker(BasePostgresService):
    def __init__(self, session: AsyncSession = None, type_provider=TypeProvider.YOOKASSA):
        self._model = Payment
        self._session = session
        self.provider = get_provider_from_user_choice(type_provider=type_provider)
        self.plan_service = get_plan_service(session=session)
        self.price_service = get_price_service(session=session)
        self.payment_provider_service = get_payment_provider_service(session=session)
        self.payment_service = get_payment_service(
            session=session,
            plan_service=self.plan_service,
            payment_provider_service=self.payment_provider_service,
        )
        self.subscription_service = get_subscription_service(
            session=session, payment_service=self.payment_service, plan_service=self.plan_service
        )
        self.type_object = yoPayment
        self.date_now = datetime.combine(datetime.utcnow(), time.max)

    async def autopayments(self) -> None:
        subscriptions = await self.get_subscriptions()
        if not subscriptions:
            logger.info("No subscriptions in need of auto-renewal were found.")
        for subscription in subscriptions:
            payment = await super().get(entity_id=subscription.payment_id)
            external_payment_id = payment.external_payment_id
            price = await self.price_service.get_one_by_filter(
                filter_={"plan_id": subscription.plan_id}
            )
            plan = await self.plan_service.get(entity_id=subscription.plan_id)
            ended_at = await self.calculationg_end_date(plan=plan)
            external_payment = await self.create_external_payment(
                payment_method_id=external_payment_id, price=price
            )
            if external_payment.status == PaymentStatusEnum.CANCELED:
                logger.info(f"Autopayment for a subscription with {subscription.id} failed.")
                return
            self._model = Payment
            payment_create = await super().create(
                entity=PaymentCreate(
                    payment_provider_id=payment.payment_provider_id,
                    payment_method=payment.payment_method,
                    status=PaymentStatusEnum.SUCCEEDED,
                    currency=external_payment.amount.currency,
                    amount=external_payment.amount.value,
                    external_payment_id=external_payment_id,
                ),
                commit=False,
            )
            await self.subscription_service.update(
                entity_id=subscription.id,
                data=Subscription(status=SubscriptionStatusEnum.ACTIVE, ended_at=ended_at),
                commit=False,
            )
            await self.session_commit()
            logger.info(f"A payment has been created with id {payment_create.id}.")
            logger.info(f"Subscriptions with {subscription.id} has been updated.")
        return

    async def get_subscriptions(self) -> list[Subscription]:
        try:
            logger.info("Uploading subscriptions from a database...")
            filter_ = (
                Subscription.status == SubscriptionStatusEnum.ACTIVE,
                Subscription.ended_at <= self.date_now,
            )
            subscriptions = await self.subscription_service.get_all(filter_=filter_)
            return subscriptions
        except AttributeError as error:
            logger.info(f"An error occurred when requesting payments from the database:{error}")

    async def create_external_payment(
        self, payment_method_id: str, price: Price
    ) -> PaymentResponse:
        try:
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
        except InvalidParamsError as error:
            logger.error(
                f"An error occurred when requesting payments from the provider: {error.detail['message']}"
            )

    async def calculationg_end_date(self, plan: Plan) -> datetime:
        duration = plan.duration
        duration_unit = plan.duration_unit
        match duration_unit:
            case DurationUnitEnum.DAY:
                return self.date_now + relativedelta(days=+duration)
            case DurationUnitEnum.MONTH:
                return self.date_now + relativedelta(months=+duration)
            case DurationUnitEnum.YEAR:
                return self.date_now + relativedelta(years=+duration)

    @rollback_transaction(method="CREATE AND UPDATE")
    async def session_commit(self) -> None:
        await self.session.commit()
        return
