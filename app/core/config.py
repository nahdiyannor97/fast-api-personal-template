import logging
from os import getenv

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=getenv(key="DOTENV_PATH", default=".env"))


class Environment:
    DEVELOPMENT: str = "DEVELOPMENT"
    PRODUCTION: str = "PRODUCTION"
    STAGING: str = "STAGING"


class Settings(BaseSettings):
    # Base settings
    environment: str = Environment.DEVELOPMENT
    project_name: str
    project_version: str

    # API version
    api_v1: str

    # Documentation Toggle
    use_static_document: bool = False

    # Database settings
    use_mock_db: bool = True

    # SQL Database settings
    database_url: str = "sqlite+aiosqlite://"
    database_echo: bool = True if environment == Environment.DEVELOPMENT else False

    # NoSQL Database settings
    database_name: str = "app_db"
    mongodb_url: str = "mongodb://"

    # Authentication settings
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate limit settings
    rate_limit_strategy: str = "fixed-window"
    rate_limit_per_minute: int = 60
    rate_limit_seconds: int = 60
    rate_limit_hour: int = 120

    # Log Settings
    log_file: str = "./logs/app.log"
    log_level: int = (
        logging.DEBUG if environment == Environment.DEVELOPMENT else logging.INFO
    )


settings = Settings()
environment = Environment()
