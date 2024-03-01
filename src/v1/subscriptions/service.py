from typing import Any, Annotated

from pydantic import BaseModel
from fastapi import Depends

from src.core.exceptions import EntityNotFoundError, InvalidParamsError
from src.core.interfaces import BasePostgresService
from src.db.postgres import DatabaseSession
from src.models import User
from src.v1.payments.models import PaymentCreate
from src.v1.plans.service import PostgresPlanService
from src.v1.subscriptions.models import Subscription, SubscriptionUpdate, SubscriptionCreate
from src.v1.payments.service import PostgresPaymentService


class SubscriptionService(BasePostgresService):
    def __init__(self, session: DatabaseSession):
        self._model = Subscription
        self._session = session
        self.payment_service: PostgresPaymentService
        self.plan_service: PostgresPlanService

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

    async def create(
        self, entity: SubscriptionCreate, user: User, return_url: str, dump_to_model: bool = True
    ) -> str:
        plan = await self.plan_service.get_one_by_filter(
            filter_={"id": entity.plan_id, "is_active": True}
        )
        if not plan:
            raise InvalidParamsError()

        amount = list(filter(lambda x: x.currency == entity.currency, plan.prices))
        if not amount or len(amount) > 1:
            raise InvalidParamsError()

        payment_create = PaymentCreate(
            plan=plan,
            payment_provider_id=entity.payment_provider_id,
            payment_method=entity.payment_method,
            currency=entity.currency,
            amount=amount[0],
        )
        payment_url = await self.payment_service.create(
            entity=payment_create, user=user, return_url=return_url
        )
        return payment_url

    async def update(
        self, entity_id: str, data: SubscriptionUpdate, dump_to_model: bool = True
    ) -> dict | Subscription:
        updated_subscription = await super().update(entity_id, data, dump_to_model)
        return updated_subscription

    async def delete(self, entity_id: Any) -> None:
        await super().delete(entity_id)


def get_subscription_service(session: DatabaseSession) -> SubscriptionService:
    return SubscriptionService(session)


PostgresSubscriptionService = Annotated[SubscriptionService, Depends(get_subscription_service)]
