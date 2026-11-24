"""Registration, login and the authenticated account (FR-001, NFR-005).

Everything goes through the public API against an in-memory database: accounts are created by
``POST /auth/register``, tokens come from ``POST /auth/login`` and are then used on protected
routes, so the whole chain (hashing, token issuing and verification, database lookup, roles) is
exercised together. Direct database access is only used to inspect results and to prepare what
the API deliberately refuses to create (administrators, suspended or password-less accounts).
"""

import logging
import time
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx2 import Response

from skillmatch.core.config import Environment, Settings
from skillmatch.core.security import create_service_token, verify_token
from skillmatch.modules.identity.models import UserRole
from skillmatch.modules.identity.passwords import PasswordHasher
from tests.api.conftest import ACCOUNT_SECRET, FAST_HASHER, TOKEN_TTL_SECONDS, UserStore

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"

PASSWORD = "correct horse battery staple"  # noqa: S105 - synthetic fixture value
WRONG_PASSWORD = "not the right password"  # noqa: S105 - synthetic fixture value
EMAIL = "ana@skillmatch.test"


def register(
    client: TestClient,
    email: str = EMAIL,
    *,
    role: str = "talento",
    password: str = PASSWORD,
) -> Response:
    """Call the public registration endpoint."""
    return client.post(REGISTER, json={"email": email, "password": password, "role": role})


def login(client: TestClient, email: str = EMAIL, password: str = PASSWORD) -> Response:
    """Call the login endpoint."""
    return client.post(LOGIN, json={"email": email, "password": password})


def token_of(client: TestClient, email: str = EMAIL, password: str = PASSWORD) -> str:
    """Log in and return the access token."""
    response = login(client, email, password)
    assert response.status_code == 200, response.text
    token: str = response.json()["access_token"]
    return token


def bearer(token: str) -> dict[str, str]:
    """Return the ``Authorization`` header for ``token``."""
    return {"Authorization": f"Bearer {token}"}


def assert_problem(response: Response, *, status: int, code: str) -> dict[str, Any]:
    """Assert an RFC 9457 problem-details response and return its body."""
    body: dict[str, Any] = response.json()
    assert response.status_code == status, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["status"] == status
    assert body["code"] == code
    return body


# --------------------------------------------------------------------------- registration


def test_a_candidate_can_register(account_client: TestClient) -> None:
    response = register(account_client, role="talento")

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "email", "role", "status", "created_at"}
    assert body["email"] == EMAIL
    assert body["role"] == "talento"
    assert body["status"] == "active"


def test_a_company_can_register(account_client: TestClient) -> None:
    response = register(account_client, "hr@skillmatch.test", role="empresa")

    assert response.status_code == 201
    assert response.json()["role"] == "empresa"


def test_the_password_is_stored_only_as_a_scrypt_hash(
    account_client: TestClient, user_store: UserStore
) -> None:
    register(account_client)

    stored = user_store.get(EMAIL)

    assert stored is not None
    assert stored.password_hash is not None
    assert stored.password_hash.startswith("$scrypt$")
    assert PASSWORD not in stored.password_hash
    assert FAST_HASHER.verify(stored.password_hash, PASSWORD) is True


def test_the_response_never_contains_the_password_or_its_hash(account_client: TestClient) -> None:
    response = register(account_client)

    assert PASSWORD not in response.text
    assert "scrypt" not in response.text
    assert "password" not in response.json()


def test_the_email_is_normalised(account_client: TestClient, user_store: UserStore) -> None:
    response = register(account_client, "  Ana@SkillMatch.TEST ")

    assert response.json()["email"] == EMAIL
    assert user_store.get(EMAIL) is not None


def test_an_email_can_only_be_registered_once_regardless_of_case_or_role(
    account_client: TestClient,
) -> None:
    assert register(account_client).status_code == 201

    duplicate = register(account_client, "ANA@skillmatch.test", role="empresa")

    assert_problem(duplicate, status=409, code="email_already_registered")


@pytest.mark.parametrize("role", ["admin", "ADMIN", "candidate", "", "superuser"])
def test_the_public_registration_cannot_create_other_roles(
    account_client: TestClient, user_store: UserStore, role: str
) -> None:
    response = register(account_client, role=role)

    body = assert_problem(response, status=422, code="validation_error")
    assert body["errors"][0]["loc"] == ["body", "role"]
    assert user_store.get(EMAIL) is None


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": PASSWORD, "role": "talento"},
        {"email": EMAIL, "password": "short", "role": "talento"},
        {"email": EMAIL, "password": " " * 20, "role": "talento"},
        {"email": EMAIL, "password": "x" * 129, "role": "talento"},
        {"email": EMAIL, "role": "talento"},
        {"password": PASSWORD, "role": "talento"},
        {"email": EMAIL, "password": PASSWORD},
        {"email": EMAIL, "password": PASSWORD, "role": "talento", "status": "suspended"},
        {"email": EMAIL, "password": PASSWORD, "role": "talento", "is_admin": True},
        {},
    ],
    ids=[
        "bad-email",
        "short-password",
        "blank-password",
        "long-password",
        "no-password",
        "no-email",
        "no-role",
        "status-injected",
        "admin-flag-injected",
        "empty-body",
    ],
)
def test_invalid_registrations_are_rejected_without_creating_an_account(
    account_client: TestClient, user_store: UserStore, payload: dict[str, Any]
) -> None:
    response = account_client.post(REGISTER, json=payload)

    assert_problem(response, status=422, code="validation_error")
    assert user_store.get(EMAIL) is None


def test_validation_errors_never_echo_the_submitted_password(account_client: TestClient) -> None:
    response = account_client.post(
        REGISTER, json={"email": "not-an-email", "password": PASSWORD, "role": "talento"}
    )

    assert response.status_code == 422
    assert PASSWORD not in response.text


# --------------------------------------------------------------------------- login


def test_login_returns_a_bearer_token_with_the_real_identity_and_role(
    account_client: TestClient, user_store: UserStore
) -> None:
    created = register(account_client, role="empresa").json()

    response = login(account_client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"  # noqa: S105
    assert body["expires_in"] == TOKEN_TTL_SECONDS
    stored = user_store.get(EMAIL)
    assert stored is not None
    assert body["user"] == {"id": created["id"], "email": EMAIL, "role": "empresa"}
    assert body["user"]["id"] == stored.id


def test_the_token_is_signed_for_the_account_and_expires_after_the_configured_lifetime(
    account_client: TestClient, account_settings: Settings
) -> None:
    created = register(account_client).json()
    before = int(time.time())

    claims = verify_token(token_of(account_client), account_settings)

    assert claims.subject == str(created["id"])
    assert claims.role == "talento"
    assert before + TOKEN_TTL_SECONDS - 5 <= claims.expires_at <= before + TOKEN_TTL_SECONDS + 5


def test_the_token_response_must_not_be_cached(account_client: TestClient) -> None:
    register(account_client)

    response = login(account_client)

    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"


def test_login_is_case_insensitive_on_the_email(account_client: TestClient) -> None:
    register(account_client)

    assert login(account_client, "ANA@SkillMatch.test").status_code == 200


def test_a_wrong_password_and_an_unknown_email_look_exactly_the_same(
    account_client: TestClient,
) -> None:
    register(account_client)

    wrong_password = login(account_client, password=WRONG_PASSWORD)
    unknown_email = login(account_client, "nobody@skillmatch.test")

    assert_problem(wrong_password, status=401, code="invalid_credentials")
    assert_problem(unknown_email, status=401, code="invalid_credentials")
    assert wrong_password.json() == unknown_email.json()
    assert "access_token" not in wrong_password.text


def test_an_inactive_account_cannot_log_in_even_with_the_right_password(
    account_client: TestClient, user_store: UserStore
) -> None:
    register(account_client)
    user_store.set_status(EMAIL, "suspended")

    response = login(account_client)

    assert_problem(response, status=401, code="invalid_credentials")
    assert response.json() == login(account_client, "nobody@skillmatch.test").json()


def test_an_account_without_a_password_cannot_log_in(
    account_client: TestClient, user_store: UserStore
) -> None:
    user_store.add(email=EMAIL, role=UserRole.TALENTO, password_hash=None)

    assert_problem(login(account_client), status=401, code="invalid_credentials")


def test_a_successful_login_records_the_time(
    account_client: TestClient, user_store: UserStore
) -> None:
    register(account_client)
    before = user_store.get(EMAIL)
    assert before is not None
    assert before.last_login_at is None

    login(account_client)

    after = user_store.get(EMAIL)
    assert after is not None
    assert after.last_login_at is not None


def test_a_failed_login_does_not_record_anything(
    account_client: TestClient, user_store: UserStore
) -> None:
    register(account_client)

    login(account_client, password=WRONG_PASSWORD)

    stored = user_store.get(EMAIL)
    assert stored is not None
    assert stored.last_login_at is None


def test_the_client_cannot_choose_the_role_at_login(account_client: TestClient) -> None:
    register(account_client, role="talento")

    response = account_client.post(
        LOGIN, json={"email": EMAIL, "password": PASSWORD, "role": "admin"}
    )

    assert_problem(response, status=422, code="validation_error")


def test_login_is_refused_when_no_signing_secret_is_configured(
    make_account_app: Callable[..., FastAPI],
) -> None:
    no_secret = Settings(environment=Environment.TEST)
    with TestClient(make_account_app(no_secret), raise_server_exceptions=False) as client:
        register(client)

        response = login(client)

    assert_problem(response, status=503, code="authentication_unavailable")
    assert "access_token" not in response.text


def test_an_outdated_password_hash_is_upgraded_at_login(
    make_account_app: Callable[..., FastAPI],
    account_settings: Settings,
    user_store: UserStore,
) -> None:
    outdated = PasswordHasher(log_n=4).hash(PASSWORD)
    user_store.add(email=EMAIL, role=UserRole.TALENTO, password_hash=outdated)
    current = PasswordHasher(log_n=5)

    with TestClient(make_account_app(account_settings, current)) as client:
        assert login(client).status_code == 200

    stored = user_store.get(EMAIL)
    assert stored is not None
    assert stored.password_hash is not None
    assert stored.password_hash != outdated
    assert current.needs_rehash(stored.password_hash) is False
    assert current.verify(stored.password_hash, PASSWORD) is True


# --------------------------------------------------------------------------- tokens


def test_the_token_identifies_the_account_on_protected_routes(account_client: TestClient) -> None:
    created = register(account_client).json()

    response = account_client.get(ME, headers=bearer(token_of(account_client)))

    assert response.status_code == 200
    assert response.json() == created


def test_protected_routes_need_a_credential(account_client: TestClient) -> None:
    assert_problem(account_client.get(ME), status=401, code="authentication_required")


def test_a_garbage_token_is_refused(account_client: TestClient) -> None:
    response = account_client.get(ME, headers=bearer("not-a-token"))

    assert_problem(response, status=401, code="invalid_credentials")


def test_an_expired_token_is_refused(account_client: TestClient) -> None:
    created = register(account_client).json()
    expired = create_service_token(
        subject=str(created["id"]),
        role="talento",
        secret=ACCOUNT_SECRET,
        expires_in=TOKEN_TTL_SECONDS,
        now=int(time.time()) - 2 * TOKEN_TTL_SECONDS,
    )

    assert account_client.get(ME, headers=bearer(expired)).status_code == 401


def test_a_token_stops_working_when_the_account_is_suspended(
    account_client: TestClient, user_store: UserStore
) -> None:
    register(account_client)
    token = token_of(account_client)
    assert account_client.get(ME, headers=bearer(token)).status_code == 200

    user_store.set_status(EMAIL, "suspended")

    assert account_client.get(ME, headers=bearer(token)).status_code == 401


# --------------------------------------------------------------------------- roles, end to end


def test_each_role_reaches_only_its_own_routes_with_a_real_login(
    account_client: TestClient, user_store: UserStore
) -> None:
    register(account_client, "talent@skillmatch.test", role="talento")
    register(account_client, "company@skillmatch.test", role="empresa")
    user_store.add(
        email="admin@skillmatch.test",
        role=UserRole.ADMIN,
        password_hash=FAST_HASHER.hash(PASSWORD),
    )
    talent = bearer(token_of(account_client, "talent@skillmatch.test"))
    company = bearer(token_of(account_client, "company@skillmatch.test"))
    admin = bearer(token_of(account_client, "admin@skillmatch.test"))

    assert account_client.get("/_probe/company-only", headers=company).status_code == 200
    assert account_client.get("/_probe/company-only", headers=talent).status_code == 403
    assert account_client.get("/_probe/company-only", headers=admin).status_code == 403
    assert account_client.get("/_probe/admin-only", headers=admin).status_code == 200
    assert account_client.get("/_probe/admin-only", headers=talent).status_code == 403
    assert account_client.get("/_probe/admin-only", headers=company).status_code == 403


def test_a_forged_role_claim_cannot_elevate_a_registered_account(
    account_client: TestClient,
) -> None:
    created = register(account_client, role="talento").json()
    forged = create_service_token(
        subject=str(created["id"]), role="admin", secret=ACCOUNT_SECRET, expires_in=600
    )

    response = account_client.get("/_probe/admin-only", headers=bearer(forged))

    assert_problem(response, status=403, code="permission_denied")


def test_the_role_comes_from_the_database_not_from_the_token(
    account_client: TestClient,
) -> None:
    register(account_client, role="talento")
    token = token_of(account_client)

    assert account_client.get("/_probe/company-only", headers=bearer(token)).status_code == 403


# --------------------------------------------------------------------------- logs


def test_registration_and_login_never_write_secrets_to_the_logs(
    account_client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)

    register(account_client)
    token = token_of(account_client)
    login(account_client, password=WRONG_PASSWORD)

    assert PASSWORD not in caplog.text
    assert WRONG_PASSWORD not in caplog.text
    assert token not in caplog.text
    assert ACCOUNT_SECRET not in caplog.text
    assert "$scrypt$" not in caplog.text
