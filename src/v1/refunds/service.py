from typing import Any, Annotated

from fastapi import Depends

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces.base import AbstractProvider
from src.core.interfaces.database import BasePostgresService
from src.db.postgres import DatabaseSession
from src.v1.payment_providers.models import PaymentProviderRefundParams
from src.v1.payment_providers.service import AbstractProviderMixin
from src.v1.payments.service import PaymentService, get_payment_service
from src.v1.plans.service import PlanService, get_plan_service
from src.v1.refunds.models import (
    Refund, RefundReason, RefundCreate, RefundReasonCreate,
    RefundReasonUpdate, RefundUpdate, RefundTicketStatusEnum
)
from src.v1.subscriptions.service import SubscriptionService, get_subscription_service
from src.v1.subscriptions.models import SubscriptionStatusEnum


class RefundReasonsService(BasePostgresService):

    def __init__(self, session: DatabaseSession):
        self._model = RefundReason
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | RefundReason:
        refund_reason = await super().get(entity_id, dump_to_model)
        return refund_reason

    async def get_one_by_filter(
        self,
        filter_: dict | tuple,
        dump_to_model: bool = True
    ) -> dict | RefundReason:
        try:
            refund_reason = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return refund_reason

    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[RefundReason]:
        refund_reasons = await super().get_all(filter_, dump_to_model)
        return refund_reasons

    async def create(
        self, entity: RefundReasonCreate, dump_to_model: bool = True
    ) -> dict | RefundReasonCreate:
        refund_reason = await super().create(entity)
        return refund_reason if dump_to_model else refund_reason.model_dump()

    async def update(
        self,
        entity_id: str,
        data: RefundReasonUpdate,
        dump_to_model: bool = True
    ) -> dict | RefundReason:
        updated_refund_reason = await super().update(entity_id, data, dump_to_model)
        return updated_refund_reason

    async def delete(self, entity_id: Any) -> None:
        await super().delete(entity_id)


class RefundService(BasePostgresService):

    def __init__(
        self,
        session: DatabaseSession,
        refund_reasons_service: RefundReasonsService,
        subscription_service: SubscriptionService
    ):
        self._model = Refund
        self._session = session
        self.refund_reasons_service = refund_reasons_service
        self.subscription_service = subscription_service

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | Refund:
        refund = await super().get(entity_id, dump_to_model)
        return refund

    async def get_one_by_filter(
        self,
        filter_: dict | tuple,
        dump_to_model: bool = True
    ) -> dict | Refund:
        try:
            refund = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return refund

    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[Refund]:
        refunds = await super().get_all(filter_, dump_to_model)
        return refunds

    async def create(
        self,
        entity: RefundCreate,
        dump_to_model: bool = True
    ) -> dict | RefundCreate:
        await self.refund_reasons_service.get(entity.reason_id)
        await self.subscription_service.get_one_by_filter(
            {"id": entity.subscription_id, "status": SubscriptionStatusEnum.ACTIVE},
            raise_on_error=True
        )
        refund = await self.get_one_by_filter(
            {"subscription_id": entity.subscription_id, "status": RefundTicketStatusEnum.OPEN}
        )
        if not refund:
            refund = await super().create(entity)
        return refund if dump_to_model else refund.model_dump()

    async def update(
        self,
        entity_id: str,
        data: RefundUpdate,
        dump_to_model: bool = True
    ) -> dict | Refund:
        updated_refund = await super().update(entity_id, data, dump_to_model)
        return updated_refund

    async def delete(self, entity_id: Any) -> None:
        await super().delete(entity_id)


def get_refund_reasons_service(session: DatabaseSession) -> RefundReasonsService:
    return RefundReasonsService(session)


def get_refund_service(
    session: DatabaseSession,
    refunds_reasons_service: RefundReasonsService = Depends(get_refund_reasons_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
) -> RefundService:
    return RefundService(session, refunds_reasons_service, subscription_service)


async def get_payment_provider_for_refund_service(
    data: PaymentProviderRefundParams,
    payment_service: PaymentService = Depends(get_payment_service),
    plan_service: PlanService = Depends(get_plan_service)
) -> AbstractProvider:
    payment = await payment_service.get_one_by_filter({"external_payment_id": data.payment_id})
    if not payment:
        raise EntityNotFoundError(message="Payment not found")
    provider = AbstractProviderMixin.get_provider(payment.payment_provider.name)
    return provider(payment_service, plan_service)


PostgresRefundsService = Annotated[RefundService, Depends(get_refund_service)]
PostgresRefundReasonsService = Annotated[RefundReasonsService, Depends(get_refund_reasons_service)]
PaymentProviderServiceForRefunds = Annotated[
    RefundReasonsService, Depends(get_payment_provider_for_refund_service)
]
