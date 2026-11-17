"""Application factory.

``create_app`` builds a fully configured FastAPI instance without import-time side effects,
which keeps tests isolated and allows several differently configured apps in one process.
Run it with ``uvicorn skillmatch.app:create_app --factory``.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from skillmatch import __version__
from skillmatch.api import health
from skillmatch.api.router import API_V1_PREFIX, api_v1_router
from skillmatch.core.config import Settings, get_settings
from skillmatch.core.errors import register_exception_handlers


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage resources that live as long as the application.

    Database engines, HTTP clients and similar resources are opened before ``yield`` and closed
    after it by the tasks that introduce them.
    """
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Configuration to use. Defaults to the settings read from the environment.

    Returns:
        A ready-to-serve application.
    """
    resolved = settings or get_settings()
    docs_enabled = resolved.docs_enabled

    app = FastAPI(
        title=resolved.app_name,
        version=__version__,
        docs_url="/docs" if docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if docs_enabled else None,
        lifespan=_lifespan,
    )
    # Make every `SettingsDep` resolve to the configuration this app was built with.
    app.dependency_overrides[get_settings] = lambda: resolved

    if resolved.cors_allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=resolved.cors_allowed_origins,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
            allow_credentials=False,
        )

    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(api_v1_router, prefix=API_V1_PREFIX)
    return app
