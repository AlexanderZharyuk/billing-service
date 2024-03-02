from typing import Any, Annotated

from fastapi import Depends
from pydantic import BaseModel
from yookassa import Payment as PPPayment
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.models.receipt import Receipt, ReceiptItem
from yookassa.domain.request import PaymentRequest
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces import (
    BasePostgresService,
    get_provider_from_user_choice,
)
from src.db.postgres import DatabaseSession
from src.core.interfaces import TypeProvider
from src.models import User
from src.v1.payment_providers.service import (
    PostgresPaymentProviderService,
)
from src.v1.payments.models import (
    Payment,
    PaymentUpdate,
    PaymentCreate,
    PaymentMetadata,
    PaymentObjectCreate,
)
from src.v1.plans import Plan
from src.v1.plans.service import PostgresPlanService


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

    @staticmethod
    def create_payment_request(
        entity: PaymentCreate,
        plan: Plan,
        user: User = None,
    ) -> PaymentRequest:
        metadata = PaymentMetadata(
            plan_id=plan.id,
            user_id=str(user.id if user else entity.user_id),
            payment_provider_id=entity.payment_provider_id,
        )

        receipt = Receipt()
        customer = (
            user.model_dump(exclude={"id", "is_superuser", "roles"})
            if user
            else {
                "user_id": str(entity.user_id),
                "phone": "79990000000",
                "email": "test@email.com",
            }
        )
        receipt.customer = {**customer}
        receipt.tax_system_code = 1
        receipt.items = [
            ReceiptItem(
                {
                    "name": plan.name,
                    "description": plan.description,
                    "quantity": 1,
                    "amount": {"value": entity.amount, "currency": entity.currency},
                    "vat_code": 1,
                    "tax_system_id": 1,
                }
            )
        ]

        builder = PaymentRequestBuilder()
        builder.set_amount({"value": entity.amount, "currency": entity.currency}).set_confirmation(
            {
                "type": ConfirmationType.REDIRECT,
                "return_url": entity.return_url if entity.return_url else "",
            }
        ).set_capture(True).set_metadata(metadata.model_dump()).set_receipt(receipt)

        if plan.is_recurring:
            builder.set_payment_method_data(
                {"type": entity.payment_method}
            ).set_save_payment_method(True)

        b = builder.build()
        return b

    async def create(
        self, entity: PaymentCreate, user: User = None, dump_to_model: bool = True
    ) -> str:
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
        pp_request = self.create_payment_request(entity=entity, plan=plan, user=user)
        pp_payment = await pp_worker.create(
            type_object=PPPayment,
            params=pp_request,
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
        await super().create(payment)
        return pp_payment.confirmation.confirmation_url

    async def update(
        self, entity_id: str, data: PaymentUpdate, dump_to_model: bool = True
    ) -> dict | Payment:
        raise NotImplementedError

    async def delete(self, entity_id: Any) -> None:
        raise NotImplementedError


def get_payment_service(
    session: DatabaseSession,
    payment_provider_service: PostgresPaymentProviderService,
    plan_service: PostgresPlanService,
) -> PaymentService:
    return PaymentService(session, payment_provider_service, plan_service)


PostgresPaymentService = Annotated[PaymentService, Depends(get_payment_service)]
