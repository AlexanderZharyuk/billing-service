import logging

from enum import Enum
from typing import Any, Union, AsyncGenerator

from requests.exceptions import HTTPError
from yookassa import Configuration, Payment, Receipt, Refund
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request import PaymentRequest
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder
from yookassa.domain.response import PaymentResponse, ReceiptResponse, RefundResponse

from src.core.interfaces.base import AbstractProvider
from src.core.config import settings
from src.core.exceptions import EntityNotFoundError, InvalidParamsError
from src.models import User
from src.v1.payments.models import PaymentMetadata, PaymentCreate
from src.v1.plans import Plan


logger = logging.getLogger(__name__)


class TypeProvider(Enum):
    YOOKASSA = "YooKassa"


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
