"""Version 1 of the public HTTP API.

Each module in ``skillmatch.modules`` exposes its own ``APIRouter``; register it here, for
example::

    from skillmatch.modules.jobs import router as jobs_router

    api_v1_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])

Breaking changes to a published contract require a new version prefix.
"""

from fastapi import APIRouter

API_V1_PREFIX = "/api/v1"

api_v1_router = APIRouter()
