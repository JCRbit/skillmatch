"""Version 1 of the public HTTP API.

Each module in ``skillmatch.modules`` exposes its own ``APIRouter``; register it here, for
example::

    from skillmatch.modules.jobs import router as jobs_router

    api_v1_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])

Breaking changes to a published contract require a new version prefix.
"""

from fastapi import APIRouter

from skillmatch.api import auth, candidates, companies, jobs

API_V1_PREFIX = "/api/v1"

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router)
api_v1_router.include_router(candidates.router)
api_v1_router.include_router(companies.router)
api_v1_router.include_router(jobs.router)
