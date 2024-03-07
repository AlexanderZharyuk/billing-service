from typing import Any, Annotated

from pydantic import BaseModel
from fastapi import Depends

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces.database import BasePostgresService
from src.db.postgres import DatabaseSession
from src.v1.prices.models import Price, PriceUpdate


class PriceService(BasePostgresService):

    def __init__(self, session: DatabaseSession):
        self._model = Price
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        price = await super().get(entity_id, dump_to_model)
        return price

    async def get_one_by_filter(
        self,
        filter_: dict | tuple,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        try:
            price = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return price

    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[Price]:
        prices = await super().get_all(dump_to_model=dump_to_model)
        return prices

    async def create(self, entity: Price, dump_to_model: bool = True) -> dict | Price:
        price = await super().create(entity)
        return price if dump_to_model else price.model_dump()

    async def update(
        self,
        entity_id: str,
        data: PriceUpdate,
        dump_to_model: bool = True
    ) -> dict | Price:
        updated_price = await super().update(entity_id, data, dump_to_model)
        return updated_price

    async def delete(self, entity_id: Any) -> None:
        await super().delete(entity_id)


def get_price_service(session: DatabaseSession) -> PriceService:
    return PriceService(session)


PostgresPriceService = Annotated[PriceService, Depends(get_price_service)]
