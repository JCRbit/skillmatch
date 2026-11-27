"""Application error model and its HTTP representation.

Domain and application code raises :class:`AppError` subclasses. They are rendered as RFC 9457
*problem details* (``application/problem+json``) so that every error returned by the API has the
same shape. Validation errors never echo the submitted input, because it may contain personal
data.
"""

from collections.abc import Mapping
from http import HTTPStatus
from typing import ClassVar

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from skillmatch.core.logging import REQUEST_ID_HEADER, get_logger

logger = get_logger("skillmatch")

PROBLEM_JSON = "application/problem+json"


class AppError(Exception):
    """Base class for errors that are safe to report to API clients.

    Subclasses define the HTTP status, a stable machine-readable ``code`` and a short ``title``.
    The optional ``detail`` is shown to the client, so it must never contain secrets or
    personal data.
    """

    status_code: ClassVar[HTTPStatus] = HTTPStatus.INTERNAL_SERVER_ERROR
    code: ClassVar[str] = "internal_error"
    title: ClassVar[str] = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        """Create the error.

        Args:
            detail: Client-safe explanation. Defaults to the class ``title``.
        """
        self.detail = detail or self.title
        super().__init__(self.detail)


class AuthenticationError(AppError):
    """The caller is not authenticated."""

    status_code = HTTPStatus.UNAUTHORIZED
    code = "authentication_required"
    title = "Authentication required"


class InvalidCredentialsError(AuthenticationError):
    """The presented credential is malformed, forged, expired or belongs to an unknown user.

    It is a distinct subclass of :class:`AuthenticationError` so that route handlers and tests can
    tell "no credential" from "credential that cannot be trusted", while both keep the 401 status.
    The detail is intentionally generic: it never reveals whether a given user exists.
    """

    status_code = HTTPStatus.UNAUTHORIZED
    code = "invalid_credentials"
    title = "Invalid credentials"


class PermissionDeniedError(AppError):
    """The caller is authenticated but not allowed to perform the action."""

    status_code = HTTPStatus.FORBIDDEN
    code = "permission_denied"
    title = "Permission denied"


class NotFoundError(AppError):
    """The requested resource does not exist or is not visible to the caller."""

    status_code = HTTPStatus.NOT_FOUND
    code = "not_found"
    title = "Resource not found"


class ConflictError(AppError):
    """The request conflicts with the current state of the resource."""

    status_code = HTTPStatus.CONFLICT
    code = "conflict"
    title = "Conflict"


def _phrase(status_code: int) -> str:
    """Return the standard reason phrase for an HTTP status code."""
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Error"


def _problem(
    *,
    status: int,
    title: str,
    code: str,
    detail: str,
    instance: str,
    errors: list[dict[str, object]] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Build an ``application/problem+json`` response."""
    body: dict[str, object] = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "code": code,
        "instance": instance,
    }
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(body, status_code=status, headers=headers, media_type=PROBLEM_JSON)


def register_exception_handlers(app: FastAPI) -> None:
    """Install handlers that turn every failure into a problem-details response.

    Args:
        app: The FastAPI application to configure.
    """

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _problem(
            status=exc.status_code,
            title=exc.title,
            code=exc.code,
            detail=exc.detail,
            instance=request.url.path,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem(
            status=exc.status_code,
            title=_phrase(exc.status_code),
            code=f"http_{exc.status_code}",
            detail=str(exc.detail),
            instance=request.url.path,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Only location, message and type are exposed: the "input" and "ctx" entries could echo
        # personal data submitted by the client.
        errors: list[dict[str, object]] = [
            {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        return _problem(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            title="Request validation failed",
            code="validation_error",
            detail="One or more request fields are invalid.",
            instance=request.url.path,
            errors=errors,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, _exc: Exception) -> JSONResponse:
        # The exception's type goes to the logs only, never its message or traceback: both can
        # carry the personal data that caused it (FR-012). The client gets a generic message.
        request_id = getattr(request.state, "request_id", None)

        logger.exception(
            "Unhandled error while processing %s %s",
            request.method,
            request.url.path,
            extra={"request_id": request_id} if request_id else {},
        )

        headers = {REQUEST_ID_HEADER: request_id} if request_id else None

        return _problem(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            title=AppError.title,
            code=AppError.code,
            detail="An unexpected error occurred.",
            instance=request.url.path,
            headers=headers,
        )
