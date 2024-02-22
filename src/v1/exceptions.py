from http import HTTPStatus

from fastapi.exceptions import HTTPException


class BaseExceptionCodes:
    """Errors codes mapping class"""

    SERVICE_ERROR: int = 1000


class ServiceError(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Service currently unavailable. Please try again later.",
    ) -> None:
        detail = {"code": BaseExceptionCodes.SERVICE_ERROR, "message": message}
        super().__init__(status_code=status_code, detail=detail)
