import logging
from typing import Any, Annotated

from fastapi import Depends
from pydantic import BaseModel

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces.database import BasePostgresService

from src.db.postgres import DatabaseSession
from src.v1.payments.models import (
    Payment,
    PaymentUpdate,
    PaymentCreate, PaymentStatusEnum,
)
from src.v1.plans.service import PostgresPlanService

logger = logging.getLogger(__name__)


class PaymentService(BasePostgresService):
    def __init__(
        self,
        session: DatabaseSession,
        plan_service: PostgresPlanService,
    ):
        self.plan_service = plan_service
        self._model = Payment
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | Payment:
        payment = await super().get(entity_id, dump_to_model)
        return payment

    async def get_one_by_filter(
        self, filter_: dict | tuple, dump_to_model: bool = True
    ) -> dict | Payment:
        try:
            payment = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return payment

    async def get_all(
        self, filter_: dict | None = None, dump_to_model: bool = True
    ) -> list[dict] | list[Payment]:
        payments = await super().get_all(dump_to_model=dump_to_model)
        return payments

    async def create(
        self,
        entity: PaymentCreate,
        dump_to_model: bool = True,
        commit: bool = True
    ) -> dict | Payment:
        payment = await super().create(entity, dump_to_model, commit)
        return payment

    async def update(
        self,
        external_payment_id: str,
        data: PaymentUpdate,
        dump_to_model: bool = True,
        commit: bool = True
    ) -> dict | Payment:
        payment = await super().get_one_by_filter(
            filter_={"external_payment_id": external_payment_id}
        )
        updated_payment = await super().update(payment.id, data, dump_to_model, commit)
        return updated_payment

    async def delete(self, entity_id: Any) -> None:
        raise NotImplementedError

    async def get_or_create(
        self,
        entity: PaymentCreate,
        dump_to_model: bool = True
    ) -> tuple[dict | Payment, bool]:
        try:
            payment = await super().get_one_by_filter(
                filter_=(
                    Payment.status == PaymentStatusEnum.CREATED,
                    Payment.external_payment_id == entity.external_payment_id
                )
            )
            created = False
        except EntityNotFoundError:
            payment = await super().create(entity, dump_to_model)
            created = True

        return payment, created


def get_payment_service(
    session: DatabaseSession,
    plan_service: PostgresPlanService,
) -> PaymentService:
    return PaymentService(session, plan_service)


PostgresPaymentService = Annotated[PaymentService, Depends(get_payment_service)]
