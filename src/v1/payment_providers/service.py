import asyncio
import logging
import uuid
from enum import Enum
from typing import Any, Annotated, AsyncGenerator, Type

from fastapi import Depends
from pydantic import BaseModel
from requests.exceptions import HTTPError
from yookassa import Configuration, Payment, Refund
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

from src.core.config import settings
from src.core.exceptions import EntityNotFoundError
from src.core.interfaces.base import AbstractProvider
from src.core.interfaces.database import BasePostgresService
from src.db.postgres import DatabaseSession
from src.db.redis import get_cache_provider
from src.db.storages import BaseCacheStorage
from src.v1.payment_providers.exceptions import PaymentProviderResponseError
from src.v1.payment_providers.models import (
    PaymentProvider,
    PaymentProviderUpdate,
    PaymentProviderRefundParams,
)
from src.v1.payments.models import PaymentCreate, PaymentMetadata
from src.v1.payments.service import PaymentService, get_payment_service
from src.v1.plans.service import PlanService, get_plan_service
from src.v1.subscriptions.models import SubscriptionPayLinkCreate

logger = logging.getLogger(__name__)


class TypeProvider(Enum):
    YOOKASSA = "YooKassa"


class PostgresPaymentProviderService(BasePostgresService):
    def __init__(self, session: DatabaseSession):
        self._model = PaymentProvider
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        payment_provider = await super().get(entity_id, dump_to_model)
        return payment_provider

    async def get_one_by_filter(
        self, filter_: dict | tuple, dump_to_model: bool = True
    ) -> dict | BaseModel:
        try:
            payment_provider = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return payment_provider

    async def get_all(
        self, filter_: dict | None = None, dump_to_model: bool = True
    ) -> list[dict] | list[PaymentProvider]:
        payment_providers = await super().get_all(dump_to_model=dump_to_model)
        return payment_providers

    async def create(
        self, entity: PaymentProvider, dump_to_model: bool = True
    ) -> dict | PaymentProvider:
        payment_provider = await super().create(entity, dump_to_model)
        return payment_provider

    async def update(
        self, entity_id: str, data: PaymentProviderUpdate, dump_to_model: bool = True
    ) -> dict | PaymentProvider:
        updated_payment_provider = await super().update(entity_id, data, dump_to_model)
        return updated_payment_provider

    async def delete(self, entity_id: Any) -> None:
        await super().delete(entity_id)


class AbstractProviderMixin:
    @classmethod
    def get_provider(cls, provider_name: str) -> Type[AbstractProvider]:
        match provider_name:
            case TypeProvider.YOOKASSA.value:
                return YooKassaPaymentProvider


class YooKassaPaymentProvider(AbstractProvider, AbstractProviderMixin):
    def __init__(
        self,
        payment_service: PaymentService,
        plan_service: PlanService,
        cache_provider: BaseCacheStorage,
    ):
        self.payment_service = payment_service
        self.plan_service = plan_service
        self.cache_provider = cache_provider
        Configuration.configure(
            secret_key=settings.yookassa_shop_secret_key, account_id=settings.yookassa_shop_id
        )

    async def get(self, type_object: Any, entity_id: Any, dump_to_model: bool = True) -> dict:
        try:
            logger.info(
                f"Trying to get object of {type_object.__name__} with id {entity_id} from YooKassa"
            )
            result = type_object.find_one(entity_id)
        except HTTPError as error:
            logger.error(
                f"Getting object of {type_object.__name__} with id {entity_id} "
                f"from YooKassa was failed. Error detail: {error}"
            )
            raise EntityNotFoundError(message=f"{entity_id} not found")
        return result if dump_to_model else dict(result)

    async def get_all(
        self, type_object: Any, params: dict | None = None, dump_to_model: bool = True
    ) -> AsyncGenerator:
        cursor = None
        while True:
            if cursor:
                params["cursor"] = cursor
            try:
                result = type_object.list(params) if params else type_object.list()
                data = result.items if dump_to_model else [dict(entity) for entity in result.items]
                yield data
                if not result.next_cursor or not params:
                    break
                else:
                    cursor = result.next_cursor
            except HTTPError:
                raise PaymentProviderResponseError

    async def create(
        self,
        type_object: Any,
        params: PaymentRequestBuilder | dict,
        idempotency_key: str = None,
        dump_to_model: bool = True,
    ) -> Payment:
        try:
            logger.info(
                f"Trying to create object of {type_object.__name__} with params: {params} "
                f"in YooKassa provider"
            )
            result = type_object.create(params, idempotency_key=idempotency_key)
        except HTTPError as error:
            logger.error(
                f"Creating object of {type_object.__name__} in YooKassa provider was failed. "
                f"Params: {params}. Details: {error}"
            )
            raise PaymentProviderResponseError
        return result if dump_to_model else dict(**result)

    async def generate_pay_link(self, params: SubscriptionPayLinkCreate):
        plan = await self.plan_service.get(params.plan_id)
        payment_amount = plan.calculate_price(currency=params.currency)

        payment = PaymentCreate(
            payment_provider_id=params.payment_provider_id,
            currency=params.currency,
            amount=payment_amount,
        )
        metadata = PaymentMetadata(
            plan_id=params.plan_id,
            user_id=params.user_id,
            payment_provider_id=params.payment_provider_id,
        )
        idempotency_key_id = f"{params.user_id}.{params.plan_id}"
        idempotency_key_value = await self.cache_provider.get(idempotency_key_id)
        if not idempotency_key_value:
            idempotency_key_value = str(uuid.uuid4())
            await self.cache_provider.set(
                idempotency_key_id, idempotency_key_value, ttl_secs=settings.idempotency_key_ttl_secs
            )

        builder = await self.build_payment(payment, metadata, plan.is_recurring, params.return_url)
        task = await asyncio.gather(
            self.create(Payment, builder, idempotency_key=idempotency_key_value)
        )
        provider_payment, *_ = task
        pay_link = provider_payment.confirmation.confirmation_url
        payment.external_payment_id = provider_payment.id
        await self.payment_service.get_or_create(payment)
        return pay_link

    async def make_refund(self, params: PaymentProviderRefundParams) -> dict:
        data = {
            "amount": {"value": params.amount, "currency": params.currency.value},
            "payment_id": params.payment_id,
        }
        task = await asyncio.gather(self.create(Refund, data))
        refund, *_ = task
        return {"operation": refund.status}

    @staticmethod
    async def build_payment(
        params: PaymentCreate,
        payment_metadata: PaymentMetadata,
        is_recurring: bool,
        return_url: str,
    ) -> PaymentRequestBuilder:
        builder = PaymentRequestBuilder()
        builder.set_amount({"value": params.amount, "currency": params.currency.value})
        builder.set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": return_url})
        builder.set_capture(True)
        builder.set_metadata(payment_metadata.model_dump(mode="json"))

        if is_recurring:
            builder.set_save_payment_method(True)
        return builder.build()


async def get_payment_provider_service(
    session: DatabaseSession,
    params: SubscriptionPayLinkCreate = Depends(),
    payment_service: PaymentService = Depends(get_payment_service),
    plan_service: PlanService = Depends(get_plan_service),
    cache_provider: BaseCacheStorage = Depends(get_cache_provider),
) -> AbstractProvider:
    payment_provider_database_service = PostgresPaymentProviderService(session)
    provider = await payment_provider_database_service.get(params.payment_provider_id)
    provider = AbstractProviderMixin.get_provider(provider.name)
    return provider(payment_service, plan_service, cache_provider)


PaymentProviderService = Annotated[
    PostgresPaymentProviderService, Depends(get_payment_provider_service)
]
