import aiohttp

from fastapi import Depends
from fastapi.security import APIKeyCookie, APIKeyHeader

from src.constants import ENV
from src.core.config import settings
from src.core.exceptions import ServiceError
from src.models import User


cookie_scheme = APIKeyCookie(name=settings.session_cookie_name, auto_error=False)
header_scheme = APIKeyHeader(name=settings.external_service_token_name, auto_error=False)


async def verify_and_get_user(token: str) -> User | None:
    user = None

    # ToDo: dirty, should be refactored
    if ENV == "dev":
        user = {
            "id": "3f8cd1fb-0cc0-4e99-ba39-9478fa007731",
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "is_superuser": False,
            "roles": ["user"],
            "phone": "79999999999",
        }
    else:
        # Auth service verifies token and return user information
        async with aiohttp.ClientSession(cookies={"access_token": token}) as session:
            async with session.post(f"{settings.auth_api_url}/verify") as resp:
                if resp.headers.get("Content-Type") != "application/json":
                    raise ServiceError

                if auth_response := await resp.json():
                    user = auth_response
    return User(**user)


async def get_current_user(token: str | None = Depends(cookie_scheme)) -> dict | None:
    """Get current user"""
    user = await verify_and_get_user(token)
    return user


def is_admin(user: User) -> bool:
    if ENV == "dev":
        return True
    if user and ("admin" in user.roles or user.is_superuser):
        return True
    return False


async def get_superuser(token: str | None = Depends(cookie_scheme)) -> bool:
    user = await verify_and_get_user(token)
    return is_admin(user)


async def is_trusted_resource(token: str = Depends(header_scheme)) -> bool:
    if ENV == "dev":
        return True
    return token == settings.trusted_service_allowed_token
