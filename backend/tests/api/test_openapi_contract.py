"""The committed ``openapi.json`` is the API contract; it must match the running application.

When this test fails after an endpoint or schema change, regenerate the contract and commit it::

    uv run python scripts/export_openapi.py
"""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from skillmatch.app import create_app
from skillmatch.core.config import Environment, Settings

CONTRACT = Path(__file__).resolve().parents[2] / "openapi.json"


def test_the_committed_contract_matches_the_application() -> None:
    generated = json.loads(json.dumps(create_app(Settings(environment=Environment.TEST)).openapi()))

    assert json.loads(CONTRACT.read_text(encoding="utf-8")) == generated, (
        "openapi.json is stale. Run: uv run python scripts/export_openapi.py"
    )


def _schema(client: TestClient) -> dict[str, Any]:
    schema: dict[str, Any] = client.get("/openapi.json").json()
    return schema


def test_the_authentication_endpoints_are_documented(account_client: TestClient) -> None:
    paths = _schema(account_client)["paths"]

    register = paths["/api/v1/auth/register"]["post"]
    login = paths["/api/v1/auth/login"]["post"]
    me = paths["/api/v1/auth/me"]["get"]
    assert {"201", "409", "422"} <= set(register["responses"])
    assert {"200", "401", "422", "503"} <= set(login["responses"])
    assert {"200", "401"} <= set(me["responses"])
    assert me["security"], "GET /auth/me must declare the bearer scheme"


def test_the_contract_says_that_admins_cannot_self_register(account_client: TestClient) -> None:
    schemas = _schema(account_client)["components"]["schemas"]

    assert schemas["PublicRole"]["enum"] == ["talento", "empresa"]
    password = schemas["RegisterRequest"]["properties"]["password"]
    assert (password["minLength"], password["maxLength"]) == (12, 128)


def test_the_login_contract_has_no_role_input_and_returns_the_identity(
    account_client: TestClient,
) -> None:
    schemas = _schema(account_client)["components"]["schemas"]

    assert "role" not in schemas["LoginRequest"]["properties"]
    assert {"access_token", "expires_in", "user"} <= set(schemas["TokenResponse"]["required"])
    assert set(schemas["AuthenticatedUser"]["properties"]) == {"id", "email", "role"}


CANDIDATE_OPERATIONS = [
    ("/api/v1/candidates/me", "post", {"201", "401", "403", "409", "422"}),
    ("/api/v1/candidates/me", "get", {"200", "401", "403", "404"}),
    ("/api/v1/candidates/me", "patch", {"200", "401", "403", "404", "422"}),
    ("/api/v1/candidates/me", "delete", {"204", "401", "403", "404"}),
    ("/api/v1/candidates/me/preferences", "put", {"200", "401", "403", "404", "422"}),
    ("/api/v1/candidates/me/visibility", "put", {"200", "401", "403", "404", "422"}),
    ("/api/v1/candidates/me/skills", "get", {"200", "401", "403", "404"}),
    ("/api/v1/candidates/me/skills", "post", {"201", "401", "403", "404", "409", "422"}),
    (
        "/api/v1/candidates/me/skills/{skill_id}",
        "patch",
        {"200", "401", "403", "404", "409", "422"},
    ),
    ("/api/v1/candidates/me/skills/{skill_id}", "delete", {"204", "401", "403", "404"}),
]


@pytest.mark.parametrize(
    ("path", "method", "statuses"),
    CANDIDATE_OPERATIONS,
    ids=[f"{method} {path}" for path, method, _ in CANDIDATE_OPERATIONS],
)
def test_the_candidate_endpoints_are_documented_and_protected(
    account_client: TestClient, path: str, method: str, statuses: set[str]
) -> None:
    operation = _schema(account_client)["paths"][path][method]

    assert statuses <= set(operation["responses"])
    assert operation["security"], f"{method.upper()} {path} must declare the bearer scheme"


def test_no_candidate_url_carries_a_candidate_identifier(account_client: TestClient) -> None:
    paths = _schema(account_client)["paths"]

    candidate_paths = [path for path in paths if path.startswith("/api/v1/candidates")]
    assert candidate_paths
    assert all(
        "{skill_id}" in path or "purpose" in path or "{" not in path for path in candidate_paths
    )


def test_the_candidate_contract_has_no_identity_fields(account_client: TestClient) -> None:
    schemas = _schema(account_client)["components"]["schemas"]
    identity = {"id", "user_id", "candidate_id", "email", "role", "status", "password_hash"}

    for name in (
        "CandidateProfileCreate",
        "CandidateProfileUpdate",
        "PreferencesUpdate",
        "VisibilityUpdate",
        "SkillCreate",
        "SkillUpdate",
    ):
        assert not identity & set(schemas[name]["properties"]), name
        assert schemas[name]["additionalProperties"] is False, name
    assert not identity & set(schemas["CandidateProfileRead"]["properties"])
