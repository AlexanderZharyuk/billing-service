from http import HTTPStatus

from fastapi.exceptions import HTTPException


class BaseExceptionCodes:
    """Errors codes mapping class"""

    ALREADY_DELETED: int = 5000


class SubscriptionAlreadyDeletedError(HTTPException):
    """Возвращаемая модель при попытке отмены уже приостановленной подписки."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Subscription already deleted.",
    ) -> None:
        detail = {"code": BaseExceptionCodes.ALREADY_DELETED, "message": message}
        super().__init__(status_code=status_code, detail=detail)
