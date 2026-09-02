"""Typed process configuration loaded from environment variables."""

from enum import StrEnum
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    )

    environment: Environment = Environment.LOCAL
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Parse environment-backed settings once per process."""
    return Settings()
