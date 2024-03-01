from typing import Any, Annotated

from pydantic import BaseModel
from fastapi import Depends

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces import BasePostgresService
from src.db.postgres import DatabaseSession
from src.v1.payment_providers.models import PaymentProvider, PaymentProviderUpdate


class PaymentProviderService(BasePostgresService):

    def __init__(self, session: DatabaseSession):
        self._model = PaymentProvider
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        payment_provider = await super().get(entity_id, dump_to_model)
        return payment_provider

    async def get_one_by_filter(
        self,
        filter_: dict | tuple,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        try:
            payment_provider = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return payment_provider

    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[PaymentProvider]:
        payment_providers = await super().get_all(dump_to_model=dump_to_model)
        return payment_providers

    async def create(self, entity: PaymentProvider, dump_to_model: bool = True) -> dict | PaymentProvider:
        payment_provider = await super().create(entity)
        return payment_provider if dump_to_model else payment_provider.model_dump()

    async def update(
        self,
        entity_id: str,
        data: PaymentProviderUpdate,
        dump_to_model: bool = True
    ) -> dict | PaymentProvider:
        updated_payment_provider = await super().update(entity_id, data, dump_to_model)
        return updated_payment_provider

    async def delete(self, entity_id: Any) -> None:
        await super().delete(entity_id)


def get_payment_provider_service(session: DatabaseSession) -> PaymentProviderService:
    return PaymentProviderService(session)


PostgresPaymentProviderService = Annotated[PaymentProviderService, Depends(get_payment_provider_service)]
