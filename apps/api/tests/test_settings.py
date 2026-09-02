"""Settings validation tests."""

import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings, get_settings
from app.main import create_app


def test_settings_use_safe_local_defaults() -> None:
    settings = Settings()

    assert settings.environment is Environment.LOCAL
    assert settings.log_level == "INFO"


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
