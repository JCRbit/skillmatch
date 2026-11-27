"""B-04: Company and vacancy CRUD.

Acceptance: a company can only edit its own vacancies.
"""

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response

from tests.api.conftest import UserStore

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
COMPANIES_ME = "/api/v1/companies/me"
JOBS = "/api/v1/jobs"
PASSWORD = "correct horse battery staple"  # noqa: S105

Headers = dict[str, str]
Account = Callable[[str, str], Headers]


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
    def _account(email: str, role: str = "empresa") -> Headers:
        if user_store.get(email) is None:
            res = account_client.post(
                REGISTER, json={"email": email, "password": PASSWORD, "role": role}
            )
            assert res.status_code == 201, res.text
        login = account_client.post(LOGIN, json={"email": email, "password": PASSWORD})
        assert login.status_code == 200, login.text
        return _bearer(login.json()["access_token"])

    return _account


def _company_body(name: str = "Acme Tech") -> dict[str, object]:
    return {
        "name": name,
        "description": "Empresa de producto.",
        "website": "https://acme.test",
        "location": "Madrid",
    }


def _vacancy_body(title: str = "Backend Junior") -> dict[str, object]:
    return {
        "title": title,
        "description": "Rol backend para producto.",
        "seniority": "junior",
        "location": "Madrid",
        "work_mode": "hybrid",
        "contract_type": "full_time",
        "salary_min": 22000,
        "salary_max": 28000,
        "salary_currency": "EUR",
        "essential_skills": ["Python", "SQL"],
        "desirable_skills": ["Docker"],
        "status": "open",
    }


def test_company_crud(account_client: TestClient, account: Account) -> None:
    headers = account("hr@acme.test", "empresa")
    created = account_client.post(COMPANIES_ME, json=_company_body(), headers=headers)
    assert created.status_code == 201, created.text
    assert created.json()["name"] == "Acme Tech"

    got = account_client.get(COMPANIES_ME, headers=headers)
    assert got.status_code == 200
    assert got.json()["id"] == created.json()["id"]

    patched = account_client.patch(COMPANIES_ME, json={"name": "Acme Labs"}, headers=headers)
    assert patched.status_code == 200
    assert patched.json()["name"] == "Acme Labs"

    deleted = account_client.delete(COMPANIES_ME, headers=headers)
    assert deleted.status_code == 204
    assert_problem(
        account_client.get(COMPANIES_ME, headers=headers), status=404, code="company_not_found"
    )


def test_vacancy_crud(account_client: TestClient, account: Account) -> None:
    headers = account("hr@acme.test", "empresa")
    assert (
        account_client.post(COMPANIES_ME, json=_company_body(), headers=headers).status_code == 201
    )

    created = account_client.post(JOBS, json=_vacancy_body(), headers=headers)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["seniority"] == "junior"
    assert body["essential_skills"] == ["Python", "SQL"]
    assert body["desirable_skills"] == ["Docker"]
    vacancy_id = body["id"]

    listed = account_client.get(JOBS, headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    got = account_client.get(f"{JOBS}/{vacancy_id}", headers=headers)
    assert got.status_code == 200

    patched = account_client.patch(
        f"{JOBS}/{vacancy_id}",
        json={"status": "closed", "desirable_skills": ["Docker", "CI/CD"]},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "closed"
    assert patched.json()["desirable_skills"] == ["Docker", "CI/CD"]

    deleted = account_client.delete(f"{JOBS}/{vacancy_id}", headers=headers)
    assert deleted.status_code == 204
    assert_problem(
        account_client.get(f"{JOBS}/{vacancy_id}", headers=headers), status=404, code="not_found"
    )


def test_company_can_only_edit_its_own_vacancies(
    account_client: TestClient, account: Account
) -> None:
    owner = account("owner@acme.test", "empresa")
    other = account("other@beta.test", "empresa")
    assert (
        account_client.post(COMPANIES_ME, json=_company_body("Acme"), headers=owner).status_code
        == 201
    )
    assert (
        account_client.post(COMPANIES_ME, json=_company_body("Beta"), headers=other).status_code
        == 201
    )

    created = account_client.post(JOBS, json=_vacancy_body(), headers=owner)
    assert created.status_code == 201
    vacancy_id = created.json()["id"]

    # other company cannot read/update/delete owner's vacancy
    assert_problem(
        account_client.get(f"{JOBS}/{vacancy_id}", headers=other), status=404, code="not_found"
    )
    assert_problem(
        account_client.patch(f"{JOBS}/{vacancy_id}", json={"title": "Hacked"}, headers=other),
        status=404,
        code="not_found",
    )
    assert_problem(
        account_client.delete(f"{JOBS}/{vacancy_id}", headers=other), status=404, code="not_found"
    )

    # owner can still update
    ok = account_client.patch(f"{JOBS}/{vacancy_id}", json={"title": "Backend Jr"}, headers=owner)
    assert ok.status_code == 200
    assert ok.json()["title"] == "Backend Jr"


def test_talento_cannot_access_company_endpoints(
    account_client: TestClient, account: Account
) -> None:
    headers = account("talent@skillmatch.test", "talento")
    res = account_client.post(COMPANIES_ME, json=_company_body(), headers=headers)
    assert_problem(res, status=403, code="permission_denied")


def test_company_patch_rejects_null_required_fields(
    account_client: TestClient, account: Account
) -> None:
    headers = account("hr@acme.test", "empresa")
    assert (
        account_client.post(COMPANIES_ME, json=_company_body(), headers=headers).status_code == 201
    )

    response = account_client.patch(COMPANIES_ME, json={"name": None}, headers=headers)
    assert_problem(response, status=422, code="validation_error")


def test_vacancy_patch_rejects_null_required_fields(
    account_client: TestClient, account: Account
) -> None:
    headers = account("hr@acme.test", "empresa")
    assert (
        account_client.post(COMPANIES_ME, json=_company_body(), headers=headers).status_code == 201
    )
    created = account_client.post(JOBS, json=_vacancy_body(), headers=headers)
    assert created.status_code == 201
    vacancy_id = created.json()["id"]

    for field in [
        "title",
        "description",
        "seniority",
        "work_mode",
        "contract_type",
        "essential_skills",
        "desirable_skills",
        "status",
    ]:
        response = account_client.patch(f"{JOBS}/{vacancy_id}", json={field: None}, headers=headers)
        assert_problem(response, status=422, code="validation_error"), field
