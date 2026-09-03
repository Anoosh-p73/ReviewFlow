"""Settings validation tests."""

import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import Environment, Settings, get_settings
from app.main import create_app


def test_settings_use_safe_local_defaults() -> None:
    settings = Settings()

    assert settings.environment is Environment.LOCAL
    assert settings.log_level == "INFO"
    assert settings.database_url.get_secret_value().endswith("/reviewflow")
    assert settings.database_timeout_seconds == 2
    assert "reviewflow-local-only" not in repr(settings)


def test_invalid_environment_setting_fails_application_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REVIEWFLOW_ENVIRONMENT", "somewhere-unknown")
    get_settings.cache_clear()

    try:
        with pytest.raises(ValidationError):
            create_app()
    finally:
        get_settings.cache_clear()


@pytest.mark.parametrize(
    "database_url",
    [
        "not-a-database-url",
        "sqlite:///reviewflow.db",
        "postgresql+psycopg://reviewflow:secret@localhost",
    ],
)
def test_invalid_database_setting_is_rejected_without_echoing_input(
    database_url: str,
) -> None:
    with pytest.raises(ValidationError) as error:
        Settings(database_url=SecretStr(database_url))

    assert database_url not in str(error.value)


@pytest.mark.parametrize("timeout_seconds", [0, 11])
def test_database_timeout_must_remain_bounded(timeout_seconds: int) -> None:
    with pytest.raises(ValidationError):
        Settings(database_timeout_seconds=timeout_seconds)
