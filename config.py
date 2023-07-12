# https://fastapi.tiangolo.com/advanced/settings/
import os
import secrets

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # to get a string like this run:
    # openssl rand -hex 32
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEFAULT_SUPERUSER_USERNAME: str = "superuser"
    DEFAULT_SUPERUSER_EMAIL: EmailStr = "super.user@example.com"
    DEFAULT_SUPERUSER_FULL_NAME: str = "Super User"
    DEFAULT_SUPERUSER_PASSWORD: str = "passw0rd"
    SQLALCHEMY_DATABASE_URL: str
    ENV: str = os.environ.get("ENV", "LOCAL")
    if ENV == "PROD":
        SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
    elif ENV == "TEST":
        SQLALCHEMY_DATABASE_URL = "sqlite:///fastapi_app_test.db"
    else:
        SQLALCHEMY_DATABASE_URL = "sqlite:///fastapi_app.db"
        # SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/fastapi_app"


# Global settings for the app
settings = Settings()
