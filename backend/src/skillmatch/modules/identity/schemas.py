"""Request and response models of the authentication endpoints.

Requests forbid unknown fields, so a client cannot smuggle in values such as ``status`` or
``is_admin``. Validation errors never echo the submitted values (see
:mod:`skillmatch.core.errors`), which matters because these bodies carry passwords.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Final, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from skillmatch.modules.identity.models import UserRole

PASSWORD_MIN_LENGTH: Final = 12
"""Minimum password length: length matters more than composition rules (NIST SP 800-63B)."""

PASSWORD_MAX_LENGTH: Final = 128
"""Maximum password length: bounds the work a single request can force on the server."""

EMAIL_MAX_LENGTH: Final = 254
"""Maximum length of an email address (RFC 5321)."""

_EMAIL_PATTERN: Final = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
"""Deliberately simple shape check; ownership of the address is not verified here."""


def _normalise_email(value: object) -> object:
    """Trim and lower-case an email so that lookups and uniqueness are case-insensitive."""
    return value.strip().lower() if isinstance(value, str) else value


Email = Annotated[
    str,
    BeforeValidator(_normalise_email),
    StringConstraints(min_length=3, max_length=EMAIL_MAX_LENGTH, pattern=_EMAIL_PATTERN),
]
"""A normalised email address."""


class PublicRole(StrEnum):
    """Roles that may be chosen at public registration.

    ``ADMIN`` is intentionally absent: administrators are never self-service. Listing only the
    two public roles here also makes the OpenAPI document say so.
    """

    TALENTO = UserRole.TALENTO.value
    EMPRESA = UserRole.EMPRESA.value

    def to_user_role(self) -> UserRole:
        """Return the matching stored role."""
        return UserRole(self.value)


class RegisterRequest(BaseModel):
    """Body of ``POST /auth/register``."""

    model_config = ConfigDict(extra="forbid")

    email: Email
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        repr=False,
        description="At least 12 characters; no composition rules.",
    )
    role: PublicRole = Field(description="`talento` (candidate) or `empresa` (company).")

    @field_validator("password")
    @classmethod
    def _not_only_whitespace(cls, value: str) -> str:
        """Refuse passwords made only of whitespace."""
        if not value.strip():
            msg = "password must not consist only of whitespace"
            raise ValueError(msg)
        return value


class LoginRequest(BaseModel):
    """Body of ``POST /auth/login``.

    There is deliberately no ``role`` field: the role always comes from the stored account.
    """

    model_config = ConfigDict(extra="forbid")

    email: Email
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH, repr=False)


class UserRead(BaseModel):
    """Public representation of an account. Never includes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    status: str
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        """Treat naive database timestamps as UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class AuthenticatedUser(BaseModel):
    """Identity returned together with a token, as read from the database."""

    id: int
    email: str
    role: UserRole


class TokenResponse(BaseModel):
    """Result of a successful login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 - OAuth 2.0 token type, not a secret
    expires_in: int = Field(description="Lifetime of the token in seconds.")
    user: AuthenticatedUser
