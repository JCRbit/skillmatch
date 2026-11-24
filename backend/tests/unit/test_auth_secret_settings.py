import pytest
from pydantic import SecretStr, ValidationError

from skillmatch.core.config import AUTH_SECRET_MIN_LENGTH, Environment, Settings


@pytest.mark.parametrize("environment", [Environment.STAGING, Environment.PRODUCTION])
def test_staging_and_production_require_a_signing_secret(environment: Environment) -> None:
    with pytest.raises(ValidationError, match="SKILLMATCH_AUTH_SERVICE_SECRET"):
        Settings(environment=environment)


@pytest.mark.parametrize("environment", [Environment.STAGING, Environment.PRODUCTION])
def test_a_short_secret_is_rejected_in_staging_and_production(environment: Environment) -> None:
    short = SecretStr("s" * (AUTH_SECRET_MIN_LENGTH - 1))

    with pytest.raises(ValidationError, match="at least 32 characters"):
        Settings(environment=environment, auth_service_secret=short)


@pytest.mark.parametrize("environment", [Environment.STAGING, Environment.PRODUCTION])
def test_a_long_enough_secret_is_accepted(environment: Environment) -> None:
    secret = SecretStr("s" * AUTH_SECRET_MIN_LENGTH)

    assert Settings(environment=environment, auth_service_secret=secret).environment is environment


@pytest.mark.parametrize("environment", [Environment.LOCAL, Environment.TEST])
def test_development_environments_start_without_a_secret(environment: Environment) -> None:
    settings = Settings(environment=environment)

    assert settings.auth_service_secret.get_secret_value() == ""


def test_the_secret_never_appears_in_the_representation() -> None:
    secret = "s" * AUTH_SECRET_MIN_LENGTH

    assert secret not in repr(Settings(auth_service_secret=SecretStr(secret)))


def test_tokens_live_fifteen_minutes_by_default() -> None:
    assert Settings().auth_token_ttl_seconds == 900
