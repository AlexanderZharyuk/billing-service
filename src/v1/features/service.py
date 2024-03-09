import logging

from typing import Annotated

from fastapi import Depends

from src.core.exceptions import EntityNotFoundError
from src.v1.features.models import Feature, FeatureCreate, FeatureUpdate
from src.core.interfaces.database import BasePostgresService
from src.db.postgres import DatabaseSession


logger = logging.getLogger(__name__)


class FeatureDatabaseService(BasePostgresService):
    """Feature service depends on PostgreSQL"""

    def __init__(self, session: DatabaseSession):
        self._model = Feature
        self._session = session

    async def get(self, entity_id: int, dump_to_model: bool = True) -> dict | Feature:
        feature = await super().get(entity_id, dump_to_model)
        return feature

    async def get_one_by_filter(
        self,
        filter_: dict | tuple,
        dump_to_model: bool = True
    ) -> dict | Feature:
        try:
            feature = await super().get_one_by_filter(filter_, dump_to_model)
        except EntityNotFoundError:
            return None if dump_to_model else {}
        return feature

    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[Feature]:
        plans = await super().get_all(filter_, dump_to_model)
        return plans

    async def create(
        self,
        entity: FeatureCreate,
        dump_to_model: bool = True,
        commit: bool = True
    ) -> dict | Feature:
        plan = await super().create(entity, dump_to_model, commit)
        return plan if dump_to_model else plan.model_dump()

    async def update(
        self,
        entity_id: str,
        data: FeatureUpdate,
        dump_to_model: bool = True,
        commit: bool = True
    ) -> dict | Feature:
        updated_plan = await super().update(entity_id, data, dump_to_model, commit)
        return updated_plan

    async def delete(self, entity_id: int | str) -> None:
        await super().delete(entity_id)


def get_plan_service(session: DatabaseSession) -> FeatureDatabaseService:
    return FeatureDatabaseService(session)


PostgresFeatureService = Annotated[FeatureDatabaseService, Depends(get_plan_service)]
