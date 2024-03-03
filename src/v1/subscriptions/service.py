import datetime
import logging
from typing import Any, Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel

from src.core.exceptions import EntityNotFoundError, InvalidParamsError
from src.core.interfaces import BasePostgresService
from src.db.postgres import DatabaseSession
from src.models import User
from src.v1.payments.models import PaymentApiCreate
from src.v1.payments.service import PostgresPaymentService
from src.v1.plans.service import PostgresPlanService
from src.v1.subscriptions.models import (
    Subscription,
    SubscriptionPause,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionCancel,
    SubscriptionApiCreate,
    SubscriptionStatusEnum,
)

logger = logging.getLogger(__name__)


class SubscriptionService(BasePostgresService):
    def __init__(
        self,
        session: DatabaseSession,
        payment_service: PostgresPaymentService,
        plan_service: PostgresPlanService,
    ):
        self._model = Subscription
        self._session = session
        self.payment_service = payment_service
        self.plan_service = plan_service

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        subscription = await super().get(entity_id, dump_to_model)
        return subscription

    async def get_one_by_filter(
        self, filter_: dict, dump_to_model: bool = True
    ) -> dict | BaseModel:
        try:
            subscription = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return subscription

    async def get_all(
        self, filter_: dict | None = None, dump_to_model: bool = True
    ) -> list[dict] | list[Subscription]:
        subscriptions = await super().get_all(dump_to_model=dump_to_model)
        return subscriptions

    async def create_api(
        self, entity: SubscriptionApiCreate, user: User = None
    ) -> str:
        plan = await self.plan_service.get_one_by_filter(
            filter_={"id": entity.plan_id, "is_active": True}
        )
        if not plan:
            raise InvalidParamsError(message="Plan not found")

        amount = list(filter(lambda x: x.currency == entity.currency, plan.prices))
        if not amount or len(amount) > 1:
            raise InvalidParamsError(message="Price not found")

        payment_create = PaymentApiCreate(
            plan_id=plan.id,
            payment_provider_id=entity.payment_provider_id,
            payment_method=entity.payment_method,
            currency=entity.currency,
            amount=amount[0].amount,
            user_id=user.id if user else entity.user_id,
            return_url=entity.return_url,
        )
        confirmation_url, payment = await self.payment_service.create(
            entity=payment_create,
            user=user,
        )
        return confirmation_url

    async def create_webhook(self, external_payment_id: str | UUID, user_id: UUID, plan_id: int):
        payment = await self.payment_service.get_one_by_filter(
            filter_={"external_payment_id": external_payment_id}
        )
        if not payment:
            raise InvalidParamsError(message="Payment not found")

        subscription = SubscriptionCreate(
            user_id=user_id,
            status=SubscriptionStatusEnum.ACTIVE,
            started_at=datetime.datetime.utcnow(),
            ended_at=datetime.datetime.utcnow() + datetime.timedelta(days=31),
            plan_id=plan_id,
            payment_id=payment.id,
        )
        subscription = await self.create(entity=subscription)
        return subscription

    async def create(
        self, entity: SubscriptionCreate, dump_to_model: bool = True
    ) -> dict | Subscription:
        subscription = await super().create(entity)
        logger.debug(
            "Создана подписка в БД. ID подписки %s, ID плана %s, ID платежа %s",
            subscription.id,
            subscription.plan_id,
            subscription.payment_id,
        )
        return subscription if dump_to_model else subscription.model_dump()

    async def update(
        self,
        entity_id: str,
        data: SubscriptionPause,
        user: User | None = None,
        dump_to_model: bool = True,
    ) -> dict | Subscription:
        if user:
            subscription = await self.get_one_by_filter(
                filter_={"id": entity_id, "user_id": user.id}
            )
            if not subscription:
                raise EntityNotFoundError(message="Subscription not found")

        subscription = await self.get(entity_id, dump_to_model)
        new_ended_at = subscription.ended_at + datetime.timedelta(days=data.pause_duration_days)
        update_data = SubscriptionUpdate(
            status=data.status,
            ended_at=new_ended_at,
        )
        updated_subscription = await super().update(entity_id, update_data, dump_to_model)
        logger.debug(
            "Изменена подписка в БД. ID подписки %s, статус %s, дата окончания %s",
            subscription.id,
            data.status,
            new_ended_at,
        )
        return updated_subscription

    async def delete(
        self,
        entity_id: Any,
        user: User | None = None,
    ) -> dict | Subscription:
        if user:
            subscription = await self.get_one_by_filter(
                filter_={"id": entity_id, "user_id": user.id}
            )
            if not subscription:
                raise EntityNotFoundError(message="Subscription not found")

        canceled_subscription = await super().update(entity_id, SubscriptionCancel())
        logger.debug("Отменена подписка в БД. ID подписки %s", canceled_subscription.id)
        return canceled_subscription


def get_subscription_service(
    session: DatabaseSession,
    payment_service: PostgresPaymentService,
    plan_service: PostgresPlanService,
) -> SubscriptionService:
    return SubscriptionService(session, payment_service, plan_service)


PostgresSubscriptionService = Annotated[SubscriptionService, Depends(get_subscription_service)]
