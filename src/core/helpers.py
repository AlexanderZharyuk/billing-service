import logging
from functools import wraps
from typing import Callable

from sqlalchemy.exc import SQLAlchemyError

from src.core.exceptions import ServiceError


logger = logging.getLogger(__name__)


def rollback_transaction(method: str):
    """Rollback transaction if it was failed"""

    def inner(function: Callable):
        @wraps(function)
        async def wrapper(cls, *args, **kwargs):
            try:
                return await function(cls, *args, **kwargs)
            except SQLAlchemyError as error:
                logger.error(
                    f"Can't commit transaction for model: {cls.model.__name__}. Method: {method}. "
                    f"Exception: {error}"
                )
                await cls.session.rollback()
                raise ServiceError
        return wrapper
    return inner
