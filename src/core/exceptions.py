from http import HTTPStatus

from fastapi.exceptions import HTTPException


class BaseExceptionCodes:
    """Errors codes mapping class"""

    SERVICE_ERROR: int = 1000
    ENTITY_NOT_FOUND: int = 1001
    MULTIPLE_ENTITIES_FOUND: int = 1002
    INVALID_PARAMS: int = 1003


class ServiceError(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Service currently unavailable. Please try again later.",
    ) -> None:
        detail = {"code": BaseExceptionCodes.SERVICE_ERROR, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class EntityNotFoundError(HTTPException):
    """Возвращаемая модель при отсутствии искомого объекта."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Entity not found.",
    ) -> None:
        detail = {"code": BaseExceptionCodes.ENTITY_NOT_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class MultipleEntitiesFoundError(HTTPException):
    """Возвращаемая модель при возвращении нескольких объектах."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Multiple enities found.",
    ) -> None:
        detail = {"code": BaseExceptionCodes.MULTIPLE_ENTITIES_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class InvalidParamsError(HTTPException):
    """Возвращаемая модель при возвращении нескольких объектах."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Invalid params.",
    ) -> None:
        detail = {"code": BaseExceptionCodes.INVALID_PARAMS, "message": message}
        super().__init__(status_code=status_code, detail=detail)
