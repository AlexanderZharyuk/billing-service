from functools import cached_property, lru_cache
from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict

import src.constants as const
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    listen_addr: str = "0.0.0.0"
    listen_port: int = 8000
    allowed_hosts: list = const.DEFAULT_ALLOWED_HOSTS

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "billing_db"
    postgres_user: str = "user"
    postgres_password: str = "password"

    session_cookie_name: str = "access"
    external_service_token_name: str = "token_id"
    auth_api_url: str = "http://localhost:8002/users"
    trusted_service_allowed_token: str = "casdnvufyrvuy123sdfc981231asd"

    debug: bool = False

    @cached_property
    def pg_dsn(self):
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def _get_settings():
    return Settings()


settings = _get_settings()