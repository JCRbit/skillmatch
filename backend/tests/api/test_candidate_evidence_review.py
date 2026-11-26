"""Evidence review API (S-07, US-03).

Each signal can be confirmed, corrected, or withdrawn, and every review leaves an audit trail.
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


def _create_project(account_client: TestClient, headers: Headers) -> dict[str, Any]:
    res = account_client.post(PROJECTS, json=PROJECT_BODY, headers=headers)
    assert res.status_code == 201, res.text
    data: dict[str, Any] = res.json()
    return data


def test_evidence_confirm_correct_withdraw_leaves_audit_trail(
    account_client: TestClient, ana: Headers
) -> None:
    project = _create_project(account_client, ana)
    project_id = project["id"]
    evidences_url = f"{PROJECTS}/{project_id}/evidences"

    listed = account_client.get(evidences_url, headers=ana)
    assert listed.status_code == 200, listed.text
    evidences = listed.json()
    assert evidences
    python_ev = next(e for e in evidences if e["canonical_id"] == "python")
    assert python_ev["status"] == "proposed"

    # confirm
    confirm = account_client.patch(
        f"{evidences_url}/{python_ev['id']}",
        json={"action": "confirm"},
        headers=ana,
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["status"] == "confirmed"

    # correct
    correct = account_client.patch(
        f"{evidences_url}/{python_ev['id']}",
        json={
            "action": "correct",
            "skill_label": "Python (backend)",
            "note": "Uso principal en APIs",
        },
        headers=ana,
    )
    assert correct.status_code == 200, correct.text
    corrected = correct.json()
    assert corrected["status"] == "corrected"
    assert corrected["skill_label"] == "Python (backend)"
    assert corrected["note"] == "Uso principal en APIs"

    # withdraw
    withdraw = account_client.patch(
        f"{evidences_url}/{python_ev['id']}",
        json={"action": "withdraw", "note": "No quiero mostrarla"},
        headers=ana,
    )
    assert withdraw.status_code == 200, withdraw.text
    assert withdraw.json()["status"] == "withdrawn"

    # audit trail
    audit = account_client.get(f"{evidences_url}/{python_ev['id']}/audit", headers=ana)
    assert audit.status_code == 200, audit.text
    actions = [item["action"] for item in audit.json()]
    assert actions == ["confirm", "correct", "withdraw"]
    assert audit.json()[0]["from_status"] == "proposed"
    assert audit.json()[0]["to_status"] == "confirmed"
    assert audit.json()[-1]["to_status"] == "withdrawn"


def test_evidence_review_is_owner_scoped(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    project = _create_project(account_client, ana)
    project_id = project["id"]
    evidences = account_client.get(f"{PROJECTS}/{project_id}/evidences", headers=ana).json()
    evidence_id = evidences[0]["id"]

    res = account_client.patch(
        f"{PROJECTS}/{project_id}/evidences/{evidence_id}",
        json={"action": "confirm"},
        headers=bea,
    )
    assert_problem(res, status=404, code="not_found")

    audit = account_client.get(
        f"{PROJECTS}/{project_id}/evidences/{evidence_id}/audit", headers=bea
    )
    assert_problem(audit, status=404, code="not_found")


def test_correct_action_requires_correction_field(account_client: TestClient, ana: Headers) -> None:
    project = _create_project(account_client, ana)
    project_id = project["id"]
    evidences = account_client.get(f"{PROJECTS}/{project_id}/evidences", headers=ana).json()
    evidence_id = evidences[0]["id"]

    res = account_client.patch(
        f"{PROJECTS}/{project_id}/evidences/{evidence_id}",
        json={"action": "correct"},
        headers=ana,
    )
    assert_problem(res, status=422, code="validation_error")
