"""Operational endpoints used by orchestrators and monitoring."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["operations"])


class HealthResponse(BaseModel):
    """Result of the liveness probe."""

    status: Literal["ok"] = "ok"


@router.get("/health", summary="Liveness probe")
async def health() -> HealthResponse:
    """Report that the process is running and able to serve requests.

    This probe performs no dependency checks, so a failing database never causes the
    orchestrator to restart a healthy process. Readiness and version endpoints are added by
    task P-05.
    """
    return HealthResponse()
