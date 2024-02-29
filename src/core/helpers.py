import logging
from functools import wraps
from typing import Callable

from sqlalchemy import exc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import ServiceError


logger = logging.getLogger(__name__)


def rollback_transaction(method: str):
    """Rollback transaction if it was failed"""

    def inner(function):
        @wraps(function)
        async def wrapper(cls, *args, **kwargs):
            try:
                return await function(cls, *args, **kwargs)
            except exc.SQLAlchemyError as error:
                logger.error(
                    f"Can't commit transaction for model: {cls.model.__name__}. Method: {method}. "
                    f"Exception: {error}"
                )
                await cls.session.rollback()
                raise ServiceError
        return wrapper
    return inner
