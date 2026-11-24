"""Identity-specific errors, rendered as RFC 9457 problem details by the API layer."""

from http import HTTPStatus
from typing import ClassVar

from skillmatch.core.errors import AppError, ConflictError


class EmailAlreadyRegisteredError(ConflictError):
    """An account with this email already exists."""

    code: ClassVar[str] = "email_already_registered"
    title: ClassVar[str] = "Email already registered"


class AuthenticationUnavailableError(AppError):
    """Tokens cannot be issued because the signing secret is not configured.

    The service fails closed: it never signs with an empty or default key.
    """

    status_code: ClassVar[HTTPStatus] = HTTPStatus.SERVICE_UNAVAILABLE
    code: ClassVar[str] = "authentication_unavailable"
    title: ClassVar[str] = "Authentication is temporarily unavailable"
