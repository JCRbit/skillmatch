import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from skillmatch.app import create_app
from skillmatch.core.config import Environment, Settings, get_settings


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep every test independent from the developer's shell and local ``.env`` file."""
    for name in [key for key in os.environ if key.startswith("SKILLMATCH_")]:
        monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)  # no `.env` here, so nothing is loaded implicitly
    get_settings.cache_clear()


@pytest.fixture
def settings() -> Settings:
    """Settings for the ``test`` environment."""
    return Settings(environment=Environment.TEST)


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    """Application built with the test settings."""
    return create_app(settings)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """HTTP client that also runs the application lifespan."""
    with TestClient(app) as test_client:
        yield test_client
