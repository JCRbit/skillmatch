"""Application settings loaded from the environment.

Every setting uses the ``SKILLMATCH_`` prefix (for example ``SKILLMATCH_ENVIRONMENT``) and may
also be provided through a local ``.env`` file. Secrets must never be committed: use
environment variables locally and the CI secret store in pipelines.
"""

from enum import StrEnum
from functools import lru_cache
from typing import Self

from pydantic import AliasChoices, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Deployment environments the application can run in."""

    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Typed and immutable application configuration.

    Attributes:
        app_name: Human-readable service name, shown in the OpenAPI document.
        environment: Deployment environment; drives safe defaults such as API docs exposure.
        debug: Enables verbose diagnostics. Forbidden in production.
        cors_allowed_origins: Browser origins allowed to call the API cross-origin.
        database_url: Database connection string.
        auth_service_secret: Secret used to sign and verify access tokens.
        auth_token_ttl_seconds: Lifetime of an issued access token.
    """

    model_config = SettingsConfigDict(
        env_prefix="SKILLMATCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    app_name: str = "SkillMatch API"
    environment: Environment = Environment.LOCAL
    debug: bool = False
    cors_allowed_origins: list[str] = Field(default_factory=list)

    # Añadido: Lee SKILLMATCH_DATABASE_URL o DATABASE_URL (del .env)
    database_url: str = Field(  # type: ignore[pydantic-alias]
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/skillmatch",
        validation_alias=AliasChoices(
            "SKILLMATCH_DATABASE_URL",
            "DATABASE_URL",
        ),
    )

    # --- Authentication boundary -------------------------------------------------------
    # The API never trusts a client-supplied identifier: callers present a bearer token that
    # this service verifies. See ``skillmatch.core.security``. The secret is not required at
    # start-up (a missing secret makes every protected request fail with 401), so importing the
    # settings never breaks; production deployments must set it.
    auth_service_secret: SecretStr = Field(
        default=SecretStr(""),
        description="Secret that signs and verifies access tokens.",
    )
    auth_token_ttl_seconds: int = Field(default=900, ge=1)

    @model_validator(mode="after")
    def _reject_unsafe_production_settings(self) -> Self:
        """Fail fast at start-up instead of running insecurely in production."""
        if self.environment is Environment.PRODUCTION:
            if self.debug:
                msg = "debug mode must be disabled in production"
                raise ValueError(msg)
            if "*" in self.cors_allowed_origins:
                msg = "wildcard CORS origins are not allowed in production"
                raise ValueError(msg)
        return self

    @property
    def docs_enabled(self) -> bool:
        """Whether interactive API documentation and the OpenAPI schema are exposed."""
        return self.environment is not Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance.

    The result is cached; call ``get_settings.cache_clear()`` in tests that change the
    environment.
    """
    return Settings()
