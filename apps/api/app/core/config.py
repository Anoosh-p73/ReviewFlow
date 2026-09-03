"""Typed process configuration loaded from environment variables."""

from enum import StrEnum
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

LOCAL_DATABASE_URL = (
    "postgresql+psycopg://reviewflow:reviewflow-local-only@127.0.0.1:5432/reviewflow"
)


class Environment(StrEnum):
    """Supported runtime environments."""

    LOCAL = "local"
    TEST = "test"
    PRODUCTION = "production"

    @property
    def is_local(self) -> bool:
        """Return whether developer diagnostics may be exposed."""
        return self is Environment.LOCAL


class Settings(BaseSettings):
    """Validated ReviewFlow API process settings."""

    model_config = SettingsConfigDict(
        env_prefix="REVIEWFLOW_",
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
    )

    environment: Environment = Environment.LOCAL
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: SecretStr = SecretStr(LOCAL_DATABASE_URL)
    database_timeout_seconds: int = Field(default=2, ge=1, le=10)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        """Require the one supported PostgreSQL driver and a named database."""
        try:
            url = make_url(value.get_secret_value())
        except ArgumentError as error:
            raise ValueError("must be a valid SQLAlchemy database URL") from error

        if url.drivername != "postgresql+psycopg":
            raise ValueError("must use the postgresql+psycopg driver")
        if not url.database:
            raise ValueError("must name a PostgreSQL database")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Parse environment-backed settings once per process."""
    return Settings()
