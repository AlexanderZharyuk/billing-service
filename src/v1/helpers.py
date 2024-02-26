import logging
from functools import wraps

from sqlalchemy import exc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.v1.exceptions import ServiceError

logger = logging.getLogger(__name__)


def catch_sa_errors(func):
    @wraps(func)
    async def wrapper(cls, *args, session: AsyncSession, **kwargs):
        try:
            return await func(cls, *args, session=session, **kwargs)
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError
    return wrapper
