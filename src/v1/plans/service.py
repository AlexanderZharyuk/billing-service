from typing import Any, Annotated

from pydantic import BaseModel
from fastapi import Depends

from src.core.exceptions import EntityNotFoundError
from src.core.interfaces.database import BasePostgresService
from src.db.postgres import DatabaseSession
from src.v1.plans.models import Plan, PlanUpdate


class PlanService(BasePostgresService):

    def __init__(self, session: DatabaseSession):
        self._model = Plan
        self._session = session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        plan = await super().get(entity_id, dump_to_model)
        return plan

    async def get_one_by_filter(
        self,
        filter_: dict | tuple,
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
    ) -> list[dict] | list[Plan]:
        plans = await super().get_all(filter_, dump_to_model)
        return plans

    async def create(self, entity: Plan, dump_to_model: bool = True) -> dict | Plan:
        plan = await super().create(entity)
        return plan if dump_to_model else plan.model_dump()

    async def update(
        self,
        entity_id: str,
        data: PlanUpdate,
        dump_to_model: bool = True
    ) -> dict | Plan:
        updated_plan = await super().update(entity_id, data, dump_to_model)
        return updated_plan

    async def delete(self, entity_id: Any) -> None:
        await super().delete(entity_id)


def get_plan_service(session: DatabaseSession) -> PlanService:
    return PlanService(session)


PostgresPlanService = Annotated[PlanService, Depends(get_plan_service)]
