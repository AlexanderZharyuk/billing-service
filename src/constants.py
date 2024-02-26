import os

ENV = os.environ.get("ENV", "dev")
APP_VERSION = "1.0.0"
APP_PREFIX = "Billing Service"
APP_NAME = "Billing Service"
APP_DESCRIPTION = "Сервис Биллинга"
APP_API_DOCS_TITLE = f"{APP_NAME} ({ENV.upper()})" if ENV != "dev" else APP_NAME

DEFAULT_ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
