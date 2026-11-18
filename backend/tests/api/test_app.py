from fastapi.testclient import TestClient

from skillmatch import __version__
from skillmatch.api.deps import SettingsDep
from skillmatch.app import create_app
from skillmatch.core.config import Environment, Settings


def test_openapi_schema_exposes_the_service_version(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["version"] == __version__


def test_api_documentation_is_not_exposed_in_production() -> None:
    app = create_app(Settings(environment=Environment.PRODUCTION))

    with TestClient(app) as production_client:
        assert production_client.get("/docs").status_code == 404
        assert production_client.get("/openapi.json").status_code == 404


def test_cors_allows_only_configured_origins() -> None:
    allowed = "http://localhost:5173"
    app = create_app(Settings(environment=Environment.TEST, cors_allowed_origins=[allowed]))
    headers = {"Access-Control-Request-Method": "GET"}

    with TestClient(app) as cors_client:
        ok = cors_client.options("/health", headers={**headers, "Origin": allowed})
        denied = cors_client.options("/health", headers={**headers, "Origin": "http://evil.test"})

    assert ok.headers["access-control-allow-origin"] == allowed
    assert "access-control-allow-origin" not in denied.headers


def test_cors_is_disabled_when_no_origin_is_configured(client: TestClient) -> None:
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert "access-control-allow-origin" not in response.headers


def test_settings_dependency_resolves_to_the_configuration_of_the_app() -> None:
    app = create_app(Settings(environment=Environment.TEST, app_name="Custom name"))

    @app.get("/_test/app-name")
    async def app_name(settings: SettingsDep) -> dict[str, str]:
        return {"app_name": settings.app_name}

    with TestClient(app) as test_client:
        assert test_client.get("/_test/app-name").json() == {"app_name": "Custom name"}
