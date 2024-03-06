import logging

from typing import Any

from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import EntityNotFoundError, MultipleEntitiesFoundError
from src.core.helpers import rollback_transaction
from src.core.interfaces.base import AbstractService


logger = logging.getLogger(__name__)


class BasePostgresService(AbstractService):

    @property
    def model(self):
        """Get entity model"""
        if not hasattr(self, "_model"):
            raise NotImplementedError(
                "The required attribute `model` not representing"
            )
        return self._model

    @property
    def session(self) -> AsyncSession:
        """Returns async PostgreSQL database session."""
        if not hasattr(self, "_session"):
            raise NotImplementedError(
                "The required attribute `session` representing an instance of "
                "`DatabaseProvider` is not implemented"
            )
        return self._session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        result = await self.session.get(self.model, entity_id)
        if result is None:
            logger.info(
                f"Requested entity not found. Entity id: {entity_id}. Model: {self.model.__name__}"
            )
            raise EntityNotFoundError(message=f"{self.model.__name__} not found")

        return result if dump_to_model else result.model_dump()

    async def get_one_by_filter(
        self,
        filter_: dict | tuple,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        if isinstance(filter_, dict):
            filter_ = self._build_filter(filter_)

        statement = select(self.model).filter(*filter_)
        result = await self.session.execute(statement)
        try:
            entity = result.scalar_one_or_none()
        except MultipleResultsFound:
            logger.info(
                f"Get multiple entities with filter: {filter_} but expected one. "
                f"Model: {self.model.__name__}"
            )
            raise MultipleEntitiesFoundError

        if not entity:
            raise EntityNotFoundError

        return entity if dump_to_model else entity.model_dump()

    async def get_all(
        self,
        filter_: dict | tuple | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[BaseModel]:
        statement = select(self.model)

        if filter_:
            if isinstance(filter_, dict):
                filter_ = self._build_filter(filter_)
            statement = statement.filter(*filter_)

        result = await self.session.execute(statement)
        entities = result.scalars().all()
        return entities if dump_to_model else [entity.model_dump() for entity in entities]

    @rollback_transaction(method="CREATE")
    async def create(self, entity: BaseModel, dump_to_model: bool = True) -> dict | BaseModel:
        model_to_save = self.model(**entity.model_dump())
        self.session.add(model_to_save)
        await self.session.commit()
        await self.session.flush(model_to_save)
        return model_to_save if dump_to_model else model_to_save.model_dump()

    def _build_filter(self, filter_params: dict) -> list:
        query_filter = []
        for attribute, value in filter_params.items():
            if not hasattr(self.model, attribute):
                logger.error(
                    f"Invalid filter attribute `{attribute}` for model: {self.model.__name__}"
                )
                raise AttributeError(f"Attribute {attribute} is not allowed for this model")

            attribute = getattr(self.model, attribute)
            query_filter.append(attribute == value)
        return query_filter

    @rollback_transaction(method="UPDATE")
    async def update(
        self,
        entity_id: str,
        data: BaseModel,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        entity = await self.get(entity_id)
        for attribute, value in data.model_dump(exclude_none=True).items():
            if hasattr(entity, attribute):
                setattr(entity, attribute, value)
        await self.session.commit()
        await self.session.flush(entity)

        return entity if dump_to_model else entity.model_dump()

    @rollback_transaction(method="DELETE")
    async def delete(self, entity_id: str) -> None:
        statement = delete(self.model).where(self.model.id == entity_id)
        await self.session.execute(statement)
        await self.session.commit()
