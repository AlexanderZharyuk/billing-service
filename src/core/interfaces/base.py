import logging

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from pydantic import BaseModel

from src.v1.subscriptions.models import SubscriptionPayLinkCreate


logger = logging.getLogger(__name__)


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
        filter_: dict | tuple | None = None,
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


class AbstractProvider(ABC):
    @abstractmethod
    async def get(self, type_object: Any, entity_id: Any, dump_to_model: bool = True) -> dict:
        """Returns entity by id."""

    @abstractmethod
    async def get_all(
        self, type_object: Any, params: dict | None = None, dump_to_model: bool = True
    ) -> AsyncGenerator:
        """Returns list of entity by custom filter."""

    @abstractmethod
    async def create(
        self,
        type_object: Any,
        params: dict,
        dump_to_model: bool = True,
    ) -> dict:
        """Creates entity."""

    @abstractmethod
    async def generate_pay_link(self, params: SubscriptionPayLinkCreate) -> dict:
        """Create pay link for user."""

    @abstractmethod
    async def make_refund(self, params: BaseModel) -> dict:
        """Send refund to provider."""
