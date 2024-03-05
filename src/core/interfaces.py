import logging

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Union, AsyncGenerator

from pydantic import BaseModel
from requests.exceptions import HTTPError
from sqlalchemy import select, delete
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Payment, Receipt, Refund
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request import PaymentRequest
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder
from yookassa.domain.response import PaymentResponse, ReceiptResponse, RefundResponse

from src.core.config import settings
from src.core.exceptions import EntityNotFoundError, MultipleEntitiesFoundError, InvalidParamsError
from src.core.helpers import rollback_transaction
from src.models import User
from src.v1.payments.models import PaymentMetadata, PaymentCreate
from src.v1.plans import Plan


logger = logging.getLogger(__name__)


class TypeProvider(Enum):
    YOOKASSA = "YooKassa"


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
    async def create(
            self,
            entity: BaseModel,
            dump_to_model: bool = True,
            commit: bool = True
    ) -> dict | BaseModel:
        model_to_save = self.model(**entity.model_dump())
        self.session.add(model_to_save)
        if commit:
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
        dump_to_model: bool = True,
        commit: bool = True
    ) -> dict | BaseModel:
        entity = await self.get(entity_id)
        for attribute, value in data.model_dump(exclude_none=True).items():
            if hasattr(entity, attribute):
                setattr(entity, attribute, value)
        if commit:
            await self.session.commit()
            await self.session.flush(entity)

        return entity if dump_to_model else entity.model_dump()

    @rollback_transaction(method="DELETE")
    async def delete(self, entity_id: str) -> None:
        statement = delete(self.model).where(self.model.id == entity_id)
        await self.session.execute(statement)
        await self.session.commit()


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
    async def create_payment_request(self, *args, **kwargs) -> Any:
        """Prepare payment request."""

    @classmethod
    def get_provider(cls, type_provider: TypeProvider):
        match type_provider:
            case TypeProvider.YOOKASSA:
                return BaseYookassaProvider()


class BaseYookassaProvider(AbstractProvider):
    def __init__(self):
        Configuration.configure(settings.yookassa_shop_id, settings.yookassa_shop_secret_key)

    async def get(
        self,
        type_object: Union[Payment, Receipt, Refund],
        entity_id: Any,
        dump_to_model: bool = True,
    ) -> dict:
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
        self,
        type_object: Union[Payment, Receipt, Refund],
        params: dict | None = None,
        dump_to_model: bool = True,
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
                raise InvalidParamsError

    async def create(
        self,
        type_object: Union[Payment, Receipt, Refund],
        params: Union[dict, PaymentRequest],
        idempotency_key: str | None = None,
        dump_to_model: bool = True,
    ) -> dict | Union[PaymentResponse, ReceiptResponse, RefundResponse]:
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
            raise InvalidParamsError
        return result if dump_to_model else dict(**result)

    @staticmethod
    def create_payment_request(
        entity: PaymentCreate,
        plan: Plan,
        user: User = None,
    ) -> PaymentRequest:
        metadata = PaymentMetadata(
            plan_id=plan.id,
            user_id=str(user.id if user else entity.user_id),
            payment_provider_id=entity.payment_provider_id,
        )

        builder = PaymentRequestBuilder()
        builder.set_amount(
            {"value": entity.amount, "currency": entity.currency.value}
        ).set_confirmation(
            {
                "type": ConfirmationType.REDIRECT,
                "return_url": entity.return_url if entity.return_url else "",
            }
        ).set_capture(
            True
        ).set_metadata(
            metadata.model_dump()
        )

        if plan.is_recurring:
            builder.set_payment_method_data(
                {"type": entity.payment_method.value}
            ).set_save_payment_method(True)
        return builder.build()


def get_provider_from_user_choice(type_provider: TypeProvider | Enum) -> AbstractProvider:
    return AbstractProvider.get_provider(type_provider)
