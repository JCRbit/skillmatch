"""Granular consent and withdrawal (B-05, US-08, FR-019, decision D-09).

The acceptance criterion of FR-019 is a lifecycle test, so this module walks the full life of a
decision: nothing shared by default, grant, see it, withdraw, see it stop being shared, grant
again. All of it goes through the public API against an in-memory database.
"""

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response

from skillmatch.modules.candidates.service import DEFAULT_POLICY_VERSION
from tests.api.conftest import UserStore

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
PROFILE = "/api/v1/candidates/me"
CONSENTS = f"{PROFILE}/consents"
VISIBILITY = f"{PROFILE}/visibility"

PASSWORD = "correct horse battery staple"  # noqa: S105 - synthetic fixture value
ANA = "consent.ana@skillmatch.test"
COMPANY = "consent.hr@skillmatch.test"

Headers = dict[str, str]
Account = Callable[[str], Headers]

PROFILE_BODY: dict[str, Any] = {
    "display_name": "Ana Dev",
    "summary": "Junior backend developer.",
    "city": "Madrid",
    "languages": ["es", "en"],
}


# --------------------------------------------------------------------------- helpers
@pytest.fixture
def account(account_client: TestClient, user_store: UserStore) -> Account:
    """Return a function that registers (once) and signs in an account of the given email."""

    # account_client is unauthenticated on purpose: registering through a client that already
    # holds a session hides the real status codes.

    def _account(email: str) -> Headers:
        if user_store.get(email) is None:
            created = account_client.post(
                REGISTER,
                json={
                    "email": email,
                    "password": PASSWORD,
                    "role": "empresa" if email == COMPANY else "talento",
                },
            )
            assert created.status_code == 201, created.text
        login = account_client.post(LOGIN, json={"email": email, "password": PASSWORD})
        assert login.status_code == 200, login.text
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    return _account


@pytest.fixture
def ana(account: Account, account_client: TestClient) -> Headers:
    """Headers of a signed-in candidate who already has a profile."""
    headers = account(ANA)
    created = account_client.post(PROFILE, json=PROFILE_BODY, headers=headers)
    assert created.status_code == 201, created.text
    return headers


def set_consent(
    account_client: TestClient, headers: Headers, purpose: str, *, granted: bool
) -> Response:
    """Grant or withdraw consent for one purpose."""
    return account_client.put(f"{CONSENTS}/{purpose}", json={"granted": granted}, headers=headers)


def consents_by_purpose(account_client: TestClient, headers: Headers) -> dict[str, dict[str, Any]]:
    """Return the consent list indexed by purpose."""
    response = account_client.get(CONSENTS, headers=headers)
    assert response.status_code == 200, response.text
    return {item["purpose"]: item for item in response.json()["consents"]}


# ------------------------------------------------------------------------- defaults
def test_new_profile_shares_nothing_by_default(account_client: TestClient, ana: Headers) -> None:
    """Every purpose starts denied: there is no shared profile by default (US-08)."""
    consents = consents_by_purpose(account_client, ana)
    assert set(consents) == {"discovery", "location", "skills"}
    for item in consents.values():
        assert item["granted"] is False
        assert item["granted_at"] is None
        assert item["revoked_at"] is None
        assert item["policy_version"] is None


def test_profile_is_not_discoverable_by_default(account_client: TestClient, ana: Headers) -> None:
    """The visibility flag and the consent agree from the start."""
    profile = account_client.get(PROFILE, headers=ana)
    assert profile.status_code == 200, profile.text
    assert profile.json()["visibility"]["discoverable"] is False


# ------------------------------------------------------------------- lifecycle
def test_grant_is_recorded_with_date_and_policy_version(
    account_client: TestClient, ana: Headers
) -> None:
    """Granting stores the decision, its date and the privacy text version."""
    response = set_consent(account_client, ana, "discovery", granted=True)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["granted"] is True
    assert body["granted_at"] is not None
    assert body["revoked_at"] is None
    assert body["policy_version"] == DEFAULT_POLICY_VERSION


def test_granting_discovery_makes_the_profile_discoverable(
    account_client: TestClient, ana: Headers
) -> None:
    """Consent drives the visibility flag, not the other way round."""
    assert set_consent(account_client, ana, "discovery", granted=True).status_code == 200
    profile = account_client.get(PROFILE, headers=ana)
    assert profile.json()["visibility"]["discoverable"] is True


def test_withdrawal_turns_discovery_off_immediately(
    account_client: TestClient, ana: Headers
) -> None:
    """Withdrawal is effective: the profile stops being reachable in the same request."""
    assert set_consent(account_client, ana, "discovery", granted=True).status_code == 200
    revoked = set_consent(account_client, ana, "discovery", granted=False)
    assert revoked.status_code == 200, revoked.text
    assert revoked.json()["granted"] is False
    assert revoked.json()["revoked_at"] is not None
    profile = account_client.get(PROFILE, headers=ana)
    assert profile.json()["visibility"]["discoverable"] is False


def test_full_lifecycle_grant_withdraw_regrant(account_client: TestClient, ana: Headers) -> None:
    """The FR-019 lifecycle: grant, verify, withdraw, verify, grant again."""
    granted = set_consent(account_client, ana, "discovery", granted=True).json()
    assert granted["granted"] is True
    first_granted_at = granted["granted_at"]

    withdrawn = set_consent(account_client, ana, "discovery", granted=False).json()
    assert withdrawn["granted"] is False
    assert withdrawn["revoked_at"] is not None
    assert withdrawn["granted_at"] == first_granted_at, "the grant history is kept"

    regranted = set_consent(account_client, ana, "discovery", granted=True).json()
    assert regranted["granted"] is True
    assert regranted["granted_at"] != first_granted_at, "the new grant has its own date"
    assert regranted["revoked_at"] is not None, "the past withdrawal stays visible"
    assert account_client.get(PROFILE, headers=ana).json()["visibility"]["discoverable"] is True


def test_repeating_a_decision_keeps_one_row_and_its_date(
    account_client: TestClient, ana: Headers
) -> None:
    """The endpoint is idempotent: repeating it does not move the date of the real change."""
    first = set_consent(account_client, ana, "location", granted=True).json()
    second = set_consent(account_client, ana, "location", granted=True).json()
    assert second["granted_at"] == first["granted_at"]


def test_purposes_are_independent(account_client: TestClient, ana: Headers) -> None:
    """Granting one purpose does not grant the others (that is what granular means)."""
    assert set_consent(account_client, ana, "location", granted=True).status_code == 200
    consents = consents_by_purpose(account_client, ana)
    assert consents["location"]["granted"] is True
    assert consents["skills"]["granted"] is False
    assert consents["discovery"]["granted"] is False


def test_explicit_policy_version_is_stored(account_client: TestClient, ana: Headers) -> None:
    """A client may record the exact privacy text version it saw."""
    response = account_client.put(
        f"{CONSENTS}/skills", json={"granted": True, "policy_version": "2026-12"}, headers=ana
    )
    assert response.status_code == 200, response.text
    assert response.json()["policy_version"] == "2026-12"


# ---------------------------------------------------------------------- validation
def test_granted_is_required(account_client: TestClient, ana: Headers) -> None:
    """A decision can never be sent empty: it would be an accidental grant or withdrawal."""
    response = account_client.put(f"{CONSENTS}/discovery", json={}, headers=ana)
    assert response.status_code == 422


def test_granted_must_be_a_boolean(account_client: TestClient, ana: Headers) -> None:
    """Strings are refused instead of being coerced."""
    response = account_client.put(f"{CONSENTS}/discovery", json={"granted": "yes"}, headers=ana)
    assert response.status_code == 422


def test_unknown_purpose_is_rejected(account_client: TestClient, ana: Headers) -> None:
    """The purpose must be one of the defined ones."""
    response = set_consent(account_client, ana, "everything", granted=True)
    assert response.status_code == 422


def test_unknown_field_is_rejected(account_client: TestClient, ana: Headers) -> None:
    """Unknown fields are forbidden, as everywhere else in this module."""
    response = account_client.put(
        f"{CONSENTS}/discovery", json={"granted": True, "candidate_id": 1}, headers=ana
    )
    assert response.status_code == 422


# ------------------------------------------------------------------ authorisation
def test_requires_authentication(account_client: TestClient) -> None:
    """Without a token there is no consent to read."""
    assert account_client.get(CONSENTS).status_code == 401


def test_company_role_cannot_use_the_candidate_endpoints(
    account_client: TestClient, account: Account
) -> None:
    """Consent belongs to the candidate, so any other role is refused."""
    headers = account(COMPANY)
    assert account_client.get(CONSENTS, headers=headers).status_code == 403


def test_candidate_without_profile_gets_404(account_client: TestClient, account: Account) -> None:
    """Consent needs a profile to hang from."""
    headers = account("sin.perfil@skillmatch.test")
    assert account_client.get(CONSENTS, headers=headers).status_code == 404
