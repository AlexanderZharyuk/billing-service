import logging
from typing import Any, Annotated

from fastapi import Depends
from pydantic import BaseModel
from yookassa import Payment as PPPayment

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces import (
    BasePostgresService,
    get_provider_from_user_choice,
)
from src.core.interfaces import TypeProvider
from src.db.postgres import DatabaseSession
from src.models import User
from src.v1.payment_providers.service import (
    PostgresPaymentProviderService,
)
from src.v1.payments.models import (
    Payment,
    PaymentUpdate,
    PaymentCreate,
    PaymentObjectCreate,
)
from src.v1.plans.service import PostgresPlanService

logger = logging.getLogger(__name__)


class PaymentService(BasePostgresService):
    def __init__(
        self,
        session: DatabaseSession,
        payment_provider_service: PostgresPaymentProviderService,
        plan_service: PostgresPlanService,
    ):
        self.payment_provider_service = payment_provider_service
        self.plan_service = plan_service
        self._model = Payment
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        payment = await super().get(entity_id, dump_to_model)
        return payment

    async def get_one_by_filter(
        self, filter_: dict | tuple, dump_to_model: bool = True
    ) -> dict | BaseModel:
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
        self, entity: PaymentCreate, user: User = None, dump_to_model: bool = True
    ) -> tuple[Any, BaseModel]:
        pp = await self.payment_provider_service.get_one_by_filter(
            filter_={"id": entity.payment_provider_id}
        )
        if not pp:
            raise EntityNotFoundError(message="Payment provider not found")

        plan = await self.plan_service.get_one_by_filter(
            filter_={"id": entity.plan_id, "is_active": True}
        )

        if not (pp_worker_enum := TypeProvider._value2member_map_.get(pp.name)):
            raise EntityNotFoundError(message="Payment provider worker not found")

        pp_worker = get_provider_from_user_choice(pp_worker_enum)
        pp_payment = await pp_worker.create(
            type_object=PPPayment,
            params=pp_worker.create_payment_request(entity=entity, plan=plan, user=user),
        )

        logger.debug(
            "Создан платеж в платежном провайдере. ID %s, статус %s, ID метода %s, URL подтверждения %s",
            pp_payment.id,
            pp_payment.status,
            pp_payment.payment_method.id,
            pp_payment.confirmation.confirmation_url,
        )
        payment = PaymentObjectCreate(
            payment_provider_id=entity.payment_provider_id,
            payment_method=entity.payment_method,
            currency=entity.currency,
            amount=entity.amount,
            status=pp_payment.status,
            external_payment_id=pp_payment.id,
            external_payment_type_id=pp_payment.payment_method.id,
        )

        payment_object = await super().create(payment)
        logger.debug("Создан платеж в БД. ID %s, status %s", payment_object.id, payment_object.status)
        return pp_payment.confirmation.confirmation_url, payment_object

    async def update(
        self, external_payment_id: str, data: PaymentUpdate, dump_to_model: bool = True
    ) -> dict | Payment:
        payment = await super().get_one_by_filter(
            filter_={"external_payment_id": external_payment_id}
        )
        updated_payment = await super().update(payment.id, data, dump_to_model)
        return updated_payment

    async def delete(self, entity_id: Any) -> None:
        raise NotImplementedError


def get_payment_service(
    session: DatabaseSession,
    payment_provider_service: PostgresPaymentProviderService,
    plan_service: PostgresPlanService,
) -> PaymentService:
    return PaymentService(session, payment_provider_service, plan_service)


PostgresPaymentService = Annotated[PaymentService, Depends(get_payment_service)]
