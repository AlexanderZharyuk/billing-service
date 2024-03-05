import datetime
import logging

from typing import Any, Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel

from src.core.exceptions import EntityNotFoundError, InvalidParamsError
from src.core.interfaces.database import BasePostgresService
from src.db.postgres import DatabaseSession
from src.v1.payments.service import PostgresPaymentService
from src.v1.plans.service import PostgresPlanService
from src.v1.subscriptions.models import (
    Subscription,
    SubscriptionPause,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionStatusEnum,
    UserSubscriptionCancelEnum,
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

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | Subscription:
        subscription = await super().get(entity_id, dump_to_model)
        return subscription

    async def get_one_by_filter(
        self, filter_: dict, dump_to_model: bool = True
    ) -> dict | Subscription:
        try:
            subscription = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return subscription

    async def get_all(
        self, filter_: dict | tuple | None = None, dump_to_model: bool = True
    ) -> list[dict] | list[Subscription]:
        subscriptions = await super().get_all(filter_, dump_to_model)
        return subscriptions

    async def create(
        self, entity: SubscriptionCreate, dump_to_model: bool = True
    ) -> dict | Subscription:
        plan = await self.plan_service.get_one_by_filter(
            filter_={"id": int(entity.plan_id), "is_active": True}
        )
        if not plan:
            raise InvalidParamsError(message="Plan not found")

        ended_date = entity.started_at + Subscription.get_end_time_delta(plan)
        entity.ended_at = ended_date
        subscription = await super().create(entity)
        logger.debug(
            "Создана подписка в БД. ID подписки %s, ID плана %s, ID пользователя %s",
            subscription.id,
            subscription.plan_id,
            subscription.user_id,
        )
        return subscription if dump_to_model else subscription.model_dump()

    async def pause(
        self,
        entity_id: str,
        data: SubscriptionPause,
        dump_to_model: bool = True,
    ) -> dict | Subscription:
        subscription = await self.get_one_by_filter(filter_={"id": entity_id})
        if not subscription:
            raise EntityNotFoundError(message="Subscription not found")

        subscription = await self.get(entity_id, dump_to_model)
        new_ended_at = subscription.ended_at + datetime.timedelta(days=data.pause_duration_days)
        update_data = SubscriptionUpdate(
            status=data.status,
            ended_at=new_ended_at,
        )
        return await self.update(entity_id, update_data, dump_to_model)

    async def update(
        self,
        entity_id: str,
        data: SubscriptionUpdate,
        dump_to_model: bool = True,
    ) -> dict | Subscription:
        updated_subscription = await super().update(entity_id, data, dump_to_model)
        logger.debug(
            "Изменена подписка в БД. ID подписки %s, ID пользователя %s, статус %s, дата окончания %s",
            updated_subscription.id,
            updated_subscription.user_id,
            updated_subscription.status,
            updated_subscription.ended_at,
        )
        return updated_subscription

    async def delete(self, entity_id: Any) -> dict | Subscription:
        subscription = await self.get_one_by_filter(filter_={"id": entity_id})
        if not subscription:
            raise EntityNotFoundError(message="Subscription not found")

        subscription.status = UserSubscriptionCancelEnum.CANCELED
        await self.session.commit()
        logger.debug(
            "Отменена подписка в БД. ID подписки %s, ID пользователя %s",
            subscription.id,
            subscription.user_id,
        )
        return subscription


def get_subscription_service(
    session: DatabaseSession,
    payment_service: PostgresPaymentService,
    plan_service: PostgresPlanService,
) -> SubscriptionService:
    return SubscriptionService(session, payment_service, plan_service)


PostgresSubscriptionService = Annotated[SubscriptionService, Depends(get_subscription_service)]
