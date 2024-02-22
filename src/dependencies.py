import aiohttp

from fastapi import Depends
from fastapi.security import APIKeyCookie, APIKeyHeader

from src.core.config import settings
from src.constants import ENV
from src.v1.exceptions import ServiceError


cookie_scheme = APIKeyCookie(name=settings.session_cookie_name, auto_error=False)
header_scheme = APIKeyHeader(name=settings.external_service_token_name, auto_error=False)


async def get_superuser(token: str = Depends(cookie_scheme)) -> bool:
    if ENV == "dev":
        return True

    async with aiohttp.ClientSession(cookies={"access_token": token}) as session:
        async with session.post(f"{settings.auth_api_url}/verify") as resp:
            if resp.headers.get('Content-Type') != 'application/json':
                raise ServiceError

            auth_response = await resp.json()
            if auth_response.get("status"):
                return True
    return False


async def is_trusted_resource(token: str = Depends(header_scheme)) -> bool:
    if ENV == "dev":
        return True
    return token == settings.trusted_service_allowed_token
