from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from skillmatch.core.config import Environment, Settings, get_settings


def test_defaults_are_safe_for_local_development() -> None:
    settings = Settings()

    assert settings.environment is Environment.LOCAL
    assert settings.debug is False
    assert settings.cors_allowed_origins == []
    assert settings.docs_enabled is True


def test_environment_variables_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKILLMATCH_ENVIRONMENT", "staging")
    monkeypatch.setenv("SKILLMATCH_AUTH_SERVICE_SECRET", "s" * 32)
    monkeypatch.setenv("SKILLMATCH_CORS_ALLOWED_ORIGINS", '["http://localhost:5173"]')

    settings = Settings()

    assert settings.environment is Environment.STAGING
    assert settings.cors_allowed_origins == ["http://localhost:5173"]


def test_values_are_read_from_a_dotenv_file(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SKILLMATCH_APP_NAME=From dotenv\n", encoding="utf-8")

    assert Settings().app_name == "From dotenv"


def test_settings_are_immutable() -> None:
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.debug = True  # type: ignore[misc]


def test_docs_are_disabled_in_production() -> None:
    settings = Settings(environment=Environment.PRODUCTION, auth_service_secret=SecretStr("s" * 32))

    assert settings.docs_enabled is False


def test_debug_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError, match="debug mode must be disabled"):
        Settings(environment=Environment.PRODUCTION, debug=True)


def test_wildcard_cors_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError, match="wildcard CORS"):
        Settings(environment=Environment.PRODUCTION, cors_allowed_origins=["*"])


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
