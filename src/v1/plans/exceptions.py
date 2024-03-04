from http import HTTPStatus

from fastapi.exceptions import HTTPException


class PaymentProviderExceptionCodes:
    """Errors codes mapping class"""

    PRICE_NOT_FOUND = 4000


class PlanPriceNotFoundError(HTTPException):
    """Возвращаемая модель при ошибки сервиса провайдера."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Price for this plan with provided currency does not exist.",
    ) -> None:
        detail = {"code": PaymentProviderExceptionCodes.PRICE_NOT_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)
