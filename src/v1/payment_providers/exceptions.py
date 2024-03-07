from http import HTTPStatus

from fastapi.exceptions import HTTPException


class PaymentProviderExceptionCodes:
    """Errors codes mapping class"""

    PROVIDER_ERROR = 3000


class PaymentProviderResponseError(HTTPException):
    """Возвращаемая модель при ошибки сервиса провайдера."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Payment provider service is unavailable",
    ) -> None:
        detail = {"code": PaymentProviderExceptionCodes.PROVIDER_ERROR, "message": message}
        super().__init__(status_code=status_code, detail=detail)
