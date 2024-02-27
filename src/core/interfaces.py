from abc import ABC, abstractmethod

from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy import select, delete

from src.core.exceptions import EntityNotFoundError, MultipleEntitiesFoundError


class AbstractService(ABC):

    @abstractmethod
    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        """Returns entity by id."""

    @abstractmethod
    async def get_one_by_filter(
        self,
        filter_: Any,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        """Returns entity by custom filter."""

    @abstractmethod
    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[BaseModel]:
        """Returns list of entities by filter."""

    @abstractmethod
    async def create(
        self,
        entity: BaseModel,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        """Creates entity."""

    @abstractmethod
    async def update(
        self,
        entity_id: str,
        data: BaseModel,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        """Updates entity."""

    @abstractmethod
    async def delete(self, entity_id: str) -> None:
        """Deletes entity."""


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
        """Get database session"""
        """Returns async PostgreSQL database session."""
        if not hasattr(self, "_session"):
            raise NotImplementedError(
                "The required attribute `session` representing an instance of "
                "`AsyncPostgresDatabaseProvider` is not implemented"
            )
        return self._session

    async def get(self, entity_id: Any, dump_to_model: bool = True) -> dict | BaseModel:
        result = await self.session.get(self.model, entity_id)
        if result is None:
            raise EntityNotFoundError(message=f"{self.model.__name__} not found")

        return result if dump_to_model else result.model_dump()

    async def get_one_by_filter(
        self,
        filter_: dict,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        query_filter = self._build_filter(filter_)
        statement = select(self.model).filter(*query_filter)
        result = await self.session.execute(statement)
        try:
            entity = result.scalar_one_or_none()
        except MultipleResultsFound:
            raise MultipleEntitiesFoundError

        if not entity:
            raise EntityNotFoundError

        return entity if dump_to_model else entity.model_dump()

    async def get_all(
        self,
        filter_: dict | None = None,
        dump_to_model: bool = True
    ) -> list[dict] | list[BaseModel]:
        statement = select(self.model)
        if filter_:
            query_filter = self._build_filter(filter_)
            statement = select(self.model).filter(*query_filter)
        result = await self.session.execute(statement)
        plans = result.scalars().all()
        return plans if dump_to_model else [plan.model_dump() for plan in plans]

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
                raise AttributeError(f"Attribute {attribute} is not allowed for this model")

            attribute = getattr(self.model, attribute)
            query_filter.append(attribute == value)
        return query_filter

    async def update(
        self,
        entity_id: str, data: BaseModel,
        dump_to_model: bool = True
    ) -> dict | BaseModel:
        pass

    async def delete(self, entity_id: str) -> None:
        pass
