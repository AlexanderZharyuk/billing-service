from typing import Any, Annotated

from pydantic import BaseModel
from fastapi import Depends

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces import BasePostgresService
from src.db.postgres import DatabaseSession
from src.v1.plans.models import Plan


class PlanService(BasePostgresService):

    def __init__(self, session: DatabaseSession):
        self._model = Plan
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        plan = await super().get(entity_id)
        return plan

    async def get_one_by_filter(
        self,
        filter_: Any,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        try:
            plan = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return plan

    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[BaseModel]:
        plans = await super().get_all()
        return plans

    async def create(self, entity: BaseModel, dump_to_model: bool = True) -> dict | BaseModel:
        plan = await super().create(entity)
        return plan

    async def update(
        self,
        entity_id: str,
        data: BaseModel,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        pass

    async def delete(self, entity_id: str) -> None:
        pass


def get_plan_service(session: DatabaseSession) -> PlanService:
    return PlanService(session)


PostgresPlanService = Annotated[PlanService, Depends(get_plan_service)]
