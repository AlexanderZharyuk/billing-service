from typing import Callable

from src.db.postgres import PostgresDatabaseStorage


def session_injection(func: Callable):
    async def wrapper(*args, **kwargs):
        if not args and not kwargs.get("session"):
            db = PostgresDatabaseStorage()
            session_generator = anext(db())
            session = await session_generator
            result = await func(session=session)
            return result
        return await func(*args, **kwargs)

    return wrapper
