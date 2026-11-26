"""Manual project entry and evidence proposals (S-06, US-02).

Projects are created through the authenticated candidate API. Evidence proposals are
derived deterministically from text against the local taxonomy; no code is executed.
"""

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response

from tests.api.conftest import UserStore

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
PROFILE = "/api/v1/candidates/me"
PROJECTS = "/api/v1/candidates/me/projects"

PASSWORD = "correct horse battery staple"  # noqa: S105
ANA = "ana@skillmatch.test"
BEA = "bea@skillmatch.test"

Headers = dict[str, str]
Account = Callable[[str], Headers]

PROFILE_BODY = {
    "display_name": "Ana Dev",
    "summary": "Junior backend developer.",
    "city": "Madrid",
    "languages": ["es"],
}

PROJECT_BODY = {
    "name": "API de Tareas",
    "description": "Construí una API con Python y FastAPI, usando PostgreSQL y Docker.",
    "role": "Backend Developer",
    "stack": ["Python", "FastAPI", "PostgreSQL"],
    "source_type": "manual",
    "source_url": "https://github.com/example-skillmatch/demo",
    "project_date": "2026-03-01",
}


def assert_problem(response: Response, *, status: int, code: str) -> dict[str, Any]:
    body: dict[str, Any] = response.json()
    assert response.status_code == status, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["code"] == code
    return body


def _bearer(token: str) -> Headers:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def account(account_client: TestClient, user_store: UserStore) -> Account:
    def _account(email: str) -> Headers:
        if user_store.get(email) is None:
            created = account_client.post(
                REGISTER, json={"email": email, "password": PASSWORD, "role": "talento"}
            )
            assert created.status_code == 201, created.text
        login = account_client.post(LOGIN, json={"email": email, "password": PASSWORD})
        assert login.status_code == 200, login.text
        return _bearer(login.json()["access_token"])

    return _account


@pytest.fixture
def ana(account: Account, account_client: TestClient) -> Headers:
    headers = account(ANA)
    res = account_client.post(PROFILE, json=PROFILE_BODY, headers=headers)
    assert res.status_code == 201, res.text
    return headers


@pytest.fixture
def bea(account: Account, account_client: TestClient) -> Headers:
    headers = account(BEA)
    body = {**PROFILE_BODY, "display_name": "Bea Dev"}
    res = account_client.post(PROFILE, json=body, headers=headers)
    assert res.status_code == 201, res.text
    return headers


def test_create_project_returns_proposals(account_client: TestClient, ana: Headers) -> None:
    response = account_client.post(PROJECTS, json=PROJECT_BODY, headers=ana)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "API de Tareas"
    assert body["role"] == "Backend Developer"
    assert body["stack"] == ["Python", "FastAPI", "PostgreSQL"]
    assert body["source_type"] == "manual"
    assert body["project_date"] == "2026-03-01"
    canonical_ids = {p["canonical_id"] for p in body["evidence_proposals"]}
    assert "python" in canonical_ids
    assert "fastapi" in canonical_ids
    assert "postgresql" in canonical_ids


def test_project_manual_entry_always_available(account_client: TestClient, ana: Headers) -> None:
    body: dict[str, Any] = {
        "name": "Proyecto manual sin repo",
        "description": "Experiencia de coordinación y documentación técnica en equipo.",
        "role": "Project Contributor",
        "stack": [],
        "source_type": "manual",
        "source_url": None,
        "project_date": "2025-11-15",
    }
    response = account_client.post(PROJECTS, json=body, headers=ana)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["source_url"] is None
    assert isinstance(data["evidence_proposals"], list)


def test_list_get_patch_delete_project(account_client: TestClient, ana: Headers) -> None:
    created = account_client.post(PROJECTS, json=PROJECT_BODY, headers=ana)
    assert created.status_code == 201
    project_id = created.json()["id"]

    listed = account_client.get(PROJECTS, headers=ana)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    got = account_client.get(f"{PROJECTS}/{project_id}", headers=ana)
    assert got.status_code == 200
    assert got.json()["id"] == project_id

    patched = account_client.patch(
        f"{PROJECTS}/{project_id}",
        json={"description": "Proyecto con Python, Docker y GitHub Actions."},
        headers=ana,
    )
    assert patched.status_code == 200
    canonical_ids = {p["canonical_id"] for p in patched.json()["evidence_proposals"]}
    assert "github_actions" in canonical_ids

    deleted = account_client.delete(f"{PROJECTS}/{project_id}", headers=ana)
    assert deleted.status_code == 204

    missing = account_client.get(f"{PROJECTS}/{project_id}", headers=ana)
    assert_problem(missing, status=404, code="not_found")


def test_project_ownership_is_hidden(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    created = account_client.post(PROJECTS, json=PROJECT_BODY, headers=ana)
    project_id = created.json()["id"]

    response = account_client.get(f"{PROJECTS}/{project_id}", headers=bea)
    assert_problem(response, status=404, code="not_found")


def test_project_requires_profile(account_client: TestClient, account: Account) -> None:
    headers = account("noprofile@skillmatch.test")
    response = account_client.post(PROJECTS, json=PROJECT_BODY, headers=headers)
    assert_problem(response, status=404, code="candidate_profile_not_found")
