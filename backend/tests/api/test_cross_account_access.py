"""Tests for cross-account access control (FR-001, NFR-005)."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from skillmatch.api.deps import (
    CurrentUserDep,
    get_current_user,
    verify_resource_ownership,
)
from skillmatch.app import create_app
from skillmatch.core.config import Settings
from skillmatch.modules.identity.models import User, UserRole


@pytest.fixture
def auth_app(settings: Settings) -> FastAPI:
    """Application configured with routes to test ownership checks."""
    app = create_app(settings)

    @app.get("/_test/resources/{owner_id}")
    async def get_resource(
        owner_id: int,
        current_user: CurrentUserDep,
    ) -> dict[str, int]:
        verify_resource_ownership(
            resource_owner_id=owner_id,
            current_user=current_user,
        )
        return {"owner_id": owner_id}

    @app.get("/_test/hidden-resources/{owner_id}")
    async def get_hidden_resource(
        owner_id: int,
        current_user: CurrentUserDep,
    ) -> dict[str, int]:
        verify_resource_ownership(
            resource_owner_id=owner_id,
            current_user=current_user,
            hide_if_unauthorized=True,
        )
        return {"owner_id": owner_id}

    return app


@pytest.fixture
def auth_client(auth_app: FastAPI) -> Iterator[TestClient]:
    """Test client for cross-account authorization testing."""
    with TestClient(auth_app, raise_server_exceptions=False) as client:
        yield client


def test_missing_authentication_header_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/resources/10")

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "authentication_required"


def test_own_resource_access_succeeds(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/resources/10", headers={"X-User-Id": "10"})

    assert response.status_code == 200
    assert response.json() == {"owner_id": 10}


def test_cross_account_access_returns_403_forbidden(auth_client: TestClient) -> None:
    # El usuario 20 intenta acceder al recurso perteneciente al usuario 10
    response = auth_client.get("/_test/resources/10", headers={"X-User-Id": "20"})

    assert response.status_code == 403
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == "permission_denied"
    assert body["title"] == "Permission denied"


def test_cross_account_access_returns_404_not_found_when_hidden(
    auth_client: TestClient,
) -> None:
    # El usuario 20 intenta acceder al recurso oculto perteneciente al usuario 10
    response = auth_client.get(
        "/_test/hidden-resources/10",
        headers={"X-User-Id": "20"},
    )

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == "not_found"
    assert body["title"] == "Resource not found"


def test_admin_can_access_any_resource(auth_app: FastAPI) -> None:
    # Sobrescribir la dependencia de usuario para simular un usuario ADMIN
    async def get_admin_user() -> User:
        return User(id=99, role=UserRole.ADMIN, email="admin@skillmatch.test")

    auth_app.dependency_overrides[get_current_user] = get_admin_user

    with TestClient(auth_app) as client:
        response = client.get("/_test/resources/10")
        assert response.status_code == 200
        assert response.json() == {"owner_id": 10}
