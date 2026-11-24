from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from skillmatch.app import create_app
from skillmatch.core.config import Settings
from skillmatch.core.errors import ConflictError, NotFoundError


@pytest.fixture
def failing_app(settings: Settings) -> FastAPI:
    """Application with extra routes that fail in controlled ways."""
    app = create_app(settings)

    @app.get("/_test/not-found")
    async def not_found() -> None:
        raise NotFoundError("Candidate does not exist.")

    @app.get("/_test/conflict")
    async def conflict() -> None:
        raise ConflictError

    @app.get("/_test/validated")
    async def validated(limit: int) -> dict[str, int]:
        return {"limit": limit}

    @app.get("/_test/crash")
    async def crash() -> None:
        msg = "secret internal detail"
        raise RuntimeError(msg)

    return app


@pytest.fixture
def failing_client(failing_app: FastAPI) -> Iterator[TestClient]:
    # Unhandled exceptions must be turned into a response, not re-raised into the test.
    with TestClient(failing_app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_app_errors_are_rendered_as_problem_details(failing_client: TestClient) -> None:
    response = failing_client.get("/_test/not-found")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json() == {
        "type": "about:blank",
        "title": "Resource not found",
        "status": 404,
        "detail": "Candidate does not exist.",
        "code": "not_found",
        "instance": "/_test/not-found",
    }


def test_app_error_without_detail_uses_its_title(failing_client: TestClient) -> None:
    body = failing_client.get("/_test/conflict").json()

    assert body["status"] == 409
    assert body["detail"] == "Conflict"


def test_validation_errors_do_not_echo_the_submitted_input(failing_client: TestClient) -> None:
    response = failing_client.get("/_test/validated", params={"limit": "not-a-number"})
    body = response.json()

    assert response.status_code == 422
    assert body["code"] == "validation_error"
    assert body["errors"][0]["loc"] == ["query", "limit"]
    assert "not-a-number" not in response.text


def test_unknown_routes_use_the_problem_format(failing_client: TestClient) -> None:
    response = failing_client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "http_404"


def test_unexpected_errors_never_leak_internal_details(
    failing_client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    response = failing_client.get(
        "/_test/crash",
        headers={"X-Request-ID": "trace-500"},
    )

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "trace-500"
    assert response.json()["detail"] == "An unexpected error occurred."
    assert "secret internal detail" not in response.text
    assert "secret internal detail" in caplog.text
