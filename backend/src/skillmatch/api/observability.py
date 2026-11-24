"""Request correlation and operational endpoints (task P-05).

The middleware gives every request an id, echoes it back in the ``X-Request-ID`` header and
publishes it to the logging context, so every log line of that request carries it. ``/ready``
reports whether the process can serve traffic (it checks the database); ``/version`` reports the
code that is running.
"""

import logging
import uuid
from typing import Literal

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from skillmatch import __version__
from skillmatch.api.deps import SessionDep, SettingsDep
from skillmatch.core.logging import REQUEST_ID_HEADER, request_id_var

logger = logging.getLogger(__name__)

router = APIRouter(tags=["operations"])


def _incoming_request_id(request: Request) -> str | None:
    """Return the id supplied by the caller, if it looks usable.

    A caller-supplied id is only a correlation hint, so it is length-limited and stripped of
    control characters before being echoed; it is never used for authorization.
    """
    raw = request.headers.get(REQUEST_ID_HEADER, "").strip()
    if not raw or len(raw) > 128 or not raw.isprintable():
        return None
    return raw


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a correlation id to every request and response."""

    def __init__(self, app: ASGIApp) -> None:
        """Wrap the ASGI application.

        Args:
            app: The application to wrap.
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Run the request with a request id in scope.

        Args:
            request: Incoming request.
            call_next: The rest of the middleware stack and the endpoint.

        Returns:
            The response, with the request id echoed in its headers.
        """
        request_id = _incoming_request_id(request) or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        request.state.request_id = request_id
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


class ReadinessCheck(BaseModel):
    """Result of a single readiness check."""

    status: Literal["ok", "unavailable"] = "ok"


class ReadinessResponse(BaseModel):
    """Result of the readiness probe."""

    status: Literal["ok", "unavailable"]
    checks: dict[str, ReadinessCheck]


class VersionResponse(BaseModel):
    """Code that is running, for traceability."""

    name: str
    version: str
    environment: str
    git_sha: str


async def _database_is_ready(session: SessionDep) -> bool:
    """Return whether the database answers a trivial query."""
    try:
        await session.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError):
        return False
    return True


@router.get("/ready", summary="Readiness probe")
async def ready(
    session: SessionDep,
    response: Response,
) -> ReadinessResponse:
    """Report whether this process can serve traffic.

    Unlike ``/health`` (liveness), this checks the dependencies the API cannot work without, so an
    orchestrator can take the instance out of the load balancer without restarting it. It answers
    ``503`` when a dependency is down.

    Args:
        session: Per-request database session.
        response: Response object, used to set the status code.

    Returns:
        The state of each dependency.
    """
    database_ready = await _database_is_ready(session)
    if database_ready:
        logger.info("readiness check passed", extra={"check": "database"})
    else:
        logger.warning("readiness check failed", extra={"check": "database"})
        response.status_code = 503

    return ReadinessResponse(
        status="ok" if database_ready else "unavailable",
        checks={"database": ReadinessCheck(status="ok" if database_ready else "unavailable")},
    )


@router.get("/version", summary="Running version")
async def version(settings: SettingsDep) -> VersionResponse:
    """Report the application name, version, environment and commit that is running.

    Args:
        settings: Application settings.

    Returns:
        The build identity of the process.
    """
    return VersionResponse(
        name=settings.app_name,
        version=__version__,
        environment=settings.environment.value,
        git_sha=settings.git_sha,
    )
