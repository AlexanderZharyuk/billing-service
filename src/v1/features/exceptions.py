from fastapi import status
from fastapi.exceptions import HTTPException


class FeatureExceptionCodes:
    """Errors codes mapping class"""

    FEATURE_NOT_FOUND: int = 2000


class FeatureNotFoundError(HTTPException):
    """Custom error when admittance not found."""

    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        message: str = "Object not found.",
    ) -> None:
        detail = {"code": FeatureExceptionCodes.FEATURE_NOT_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)
