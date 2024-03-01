from typing import Any, Annotated

from fastapi import Depends
from pydantic import BaseModel
from yookassa import Payment as YookassaPayment
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
from src.models import User
from src.v1.payment_providers.service import (
    PostgresPaymentProviderService,
)
from src.v1.payments.models import (
    Payment,
    PaymentUpdate,
    PaymentCreate,
    PaymentMetadata,
)
from src.v1.plans import Plan
from src.v1.plans.service import PostgresPlanService


class PaymentService(BasePostgresService):
    def __init__(self, session: DatabaseSession):
        self.payment_provider_service: PostgresPaymentProviderService
        self.plan_service: PostgresPlanService
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

    def create_payment_request(
        self, entity: PaymentCreate, payment: Payment, plan: Plan, user: User, return_url: str
    ) -> PaymentRequest:
        metadata = PaymentMetadata(
            plan_id=entity.plan_id,
            payment_id=payment.id,
            user_id=user.id,
            payment_provider_id=entity.payment_provider_id,
        )
        receipt = Receipt()
        receipt.customer = user.model_dump(exclude={"id", "is_superuser", "roles"})
        receipt.items = [
            ReceiptItem(
                {
                    "name": plan.name,
                    "description": plan.description,
                    "quantity": 1,
                    "amount": {"value": plan.price_per_unit, "currency": entity.currency},
                }
            )
        ]

        builder = PaymentRequestBuilder()
        builder.set_amount({"value": plan.price_per_unit, "currency": entity.currency}).set_confirmation(
            {
                "type": ConfirmationType.REDIRECT,
                "return_url": return_url,
            }
        ).set_capture(False).set_metadata(metadata.model_dump()).set_receipt(receipt)

        if plan.is_recurring:
            builder.set_payment_method_data({"type": entity.payment_type}).set_save_payment_method(
                True
            )

        return builder.build()

    async def create(
        self, entity: PaymentCreate, user: User, return_url: str, dump_to_model: bool = True
    ) -> str:
        # создать платеж со статусом created в БД
        payment = await super().create(entity)

        # найти провайдера по id
        payment_provider = await self.payment_provider_service.get_one_by_filter(
            filter_={"id": entity.payment_provider_id}
        )
        plan = entity.plan

        # получить воркера для работы с провайдером
        payment_provider_worker = get_provider_from_user_choice(payment_provider.name)

        # создать рекуррентный платеж в провайдере, получить id платежа и ссылку для редиректа
        payment_request = self.create_payment_request(
            entity=entity, payment=payment, plan=plan, user=user, return_url=return_url
        )
        payment_provider_payment = await payment_provider_worker.create(
            type_object=YookassaPayment,
            params=payment_request,
            idempotency_key=payment.id,
        )

        # сохранить id платежа провайдера в БД
        payment_update = PaymentUpdate(
            status=payment_provider_payment.status,
            external_payment_id=payment_provider_payment.id,
            provider_payment_type_id=payment_provider_payment.payment_method.id,
            is_provider_payment_saved=payment_provider_payment.payment_method.saved,
        )
        await super().update(payment.id, payment_update)

        # вернуть редирект на страницу платежного провайдера для оплаты
        return payment_provider_payment.confirmation.confirmation_url

    async def update(
        self, entity_id: str, data: PaymentUpdate, dump_to_model: bool = True
    ) -> dict | Payment:
        updated_payment = await super().update(entity_id, data, dump_to_model)
        return updated_payment

    async def delete(self, entity_id: Any) -> None:
        raise NotImplementedError


def get_payment_service(session: DatabaseSession) -> PaymentService:
    return PaymentService(session)


PostgresPaymentService = Annotated[PaymentService, Depends(get_payment_service)]
