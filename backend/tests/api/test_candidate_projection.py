"""Non-leakage tests of the pseudonymised projection (B-06, FR-012, US-15).

The point of these tests is not that the endpoint works, but that it **cannot** leak: they read
the raw response body and every log line, and fail if any blocked field appears. They also check
the two conditions that make a profile reachable at all (consent plus the visibility flag) and
that each field is shared under its own purpose.
"""

import asyncio
import json
import logging
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from skillmatch.core.logging import SENSITIVE_KEYS, JsonFormatter
from skillmatch.modules.candidates.models import CandidateProfile, ConsentPurpose
from skillmatch.modules.candidates.projection import ALLOWED_FIELDS, BLOCKED_FIELDS

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/candidates/me"
CONSENTS = "/api/v1/candidates/me/consents"
SKILLS = "/api/v1/candidates/me/skills"
VISIBILITY = "/api/v1/candidates/me/visibility"

PASSWORD = "correct horse battery staple"  # noqa: S105 - synthetic value

ALLOWED_ANY_STAGE: frozenset[str] = frozenset().union(*ALLOWED_FIELDS.values())
"""Every field any stage may contain, so a test can assert nothing else came back."""


class Account:
    """A registered account with its bearer headers and, for a candidate, its profile id."""

    def __init__(self, token: str) -> None:
        self.headers = {"Authorization": f"Bearer {token}"}
        self.profile_id = 0


def _register(client: TestClient, email: str, role: str) -> Account:
    """Register an account through the public API and return its bearer headers."""
    client.post(REGISTER, json={"email": email, "password": PASSWORD, "role": role})
    response = client.post(LOGIN, json={"email": email, "password": PASSWORD})
    return Account(response.json()["access_token"])


def _keys(payload: object) -> Iterator[str]:
    """Yield every key of a nested JSON value."""
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield str(key)
            yield from _keys(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _keys(item)


def _assert_no_blocked_field(payload: object, context: str) -> None:
    """Fail if any blocked field name appears anywhere inside ``payload``."""
    found = {key for key in _keys(payload) if key in BLOCKED_FIELDS}
    assert not found, f"{context} leaked blocked fields: {sorted(found)}"


def _profile_id(db: async_sessionmaker[AsyncSession], display_name: str) -> int:
    """Return the id of a profile by its pseudonym, read straight from the test database."""

    async def _query() -> int:
        async with db() as session:
            result = await session.execute(
                select(CandidateProfile.id).where(CandidateProfile.display_name == display_name)
            )
            return result.scalar_one()

    return asyncio.run(_query())


def _read(client: TestClient, company: Account, profile_id: int) -> Response:
    """Ask for one projection as a company."""
    return client.get(f"/api/v1/candidates/{profile_id}", headers=company.headers)


@pytest.fixture
def ana(account_client: TestClient, account_db: async_sessionmaker[AsyncSession]) -> Account:
    """A candidate with a profile, a skill and every purpose granted."""
    account = _register(account_client, "proj.ana@skillmatch.test", "talento")
    account_client.post(
        ME,
        json={
            "display_name": "Ana P.",
            "summary": "Backend junior",
            "city": "Madrid",
            "languages": ["es", "en"],
        },
        headers=account.headers,
    )
    account_client.put(
        VISIBILITY,
        json={"discoverable": True, "show_location": True},
        headers=account.headers,
    )
    account_client.post(
        SKILLS, json={"name": "Python", "level": "intermediate"}, headers=account.headers
    )
    for purpose in ConsentPurpose:
        account_client.put(
            f"{CONSENTS}/{purpose.value}", json={"granted": True}, headers=account.headers
        )
    account.profile_id = _profile_id(account_db, "Ana P.")
    return account


@pytest.fixture
def company(account_client: TestClient) -> Account:
    """A company account, the only role allowed to read a projection."""
    return _register(account_client, "proj.hr@skillmatch.test", "empresa")


# --------------------------------------------------------------------------- API
def test_a_shared_profile_returns_only_allowlisted_fields(
    account_client: TestClient, ana: Account, company: Account
) -> None:
    """The projection of a fully shared profile contains allowed fields and nothing else."""
    response = _read(account_client, company, ana.profile_id)

    assert response.status_code == 200
    body = json.loads(response.content)
    _assert_no_blocked_field(body, "the projection response")
    assert body["display_name"] == "Ana P."
    assert body["city"] == "Madrid"
    assert body["skills"] == [{"name": "Python", "level": "intermediate"}]
    assert set(body) <= ALLOWED_ANY_STAGE


def test_a_profile_without_discovery_consent_is_not_reachable(
    account_client: TestClient, ana: Account, company: Account
) -> None:
    """Withdrawing ``DISCOVERY`` hides the profile, and it answers like a missing one."""
    account_client.put(f"{CONSENTS}/discovery", json={"granted": False}, headers=ana.headers)

    response = _read(account_client, company, ana.profile_id)

    assert response.status_code == 404
    assert response.json()["detail"] == "Recurso no encontrado."


def test_a_profile_that_is_not_discoverable_is_not_reachable(
    account_client: TestClient, ana: Account, company: Account
) -> None:
    """The visibility flag is an independent barrier on top of the consent."""
    account_client.put(
        VISIBILITY,
        json={"discoverable": False, "show_location": True},
        headers=ana.headers,
    )

    assert _read(account_client, company, ana.profile_id).status_code == 404


def test_a_missing_profile_answers_the_same_as_a_hidden_one(
    account_client: TestClient, company: Account
) -> None:
    """A company cannot tell a hidden profile from one that does not exist."""
    assert _read(account_client, company, 999_999).status_code == 404


def test_withdrawing_location_hides_the_city_only(
    account_client: TestClient, ana: Account, company: Account
) -> None:
    """Each field is shared under its own purpose."""
    account_client.put(f"{CONSENTS}/location", json={"granted": False}, headers=ana.headers)

    body = _read(account_client, company, ana.profile_id).json()

    assert "city" not in body
    assert body["display_name"] == "Ana P."
    _assert_no_blocked_field(body, "the projection without location")


def test_withdrawing_skills_hides_the_skills_only(
    account_client: TestClient, ana: Account, company: Account
) -> None:
    """The ``SKILLS`` purpose removes the skill list and nothing else."""
    account_client.put(f"{CONSENTS}/skills", json={"granted": False}, headers=ana.headers)

    body = _read(account_client, company, ana.profile_id).json()

    assert "skills" not in body
    assert body["city"] == "Madrid"
    _assert_no_blocked_field(body, "the projection without skills")


def test_show_location_off_hides_the_city(
    account_client: TestClient, ana: Account, company: Account
) -> None:
    """The candidate's own flag can hide the city even with the purpose granted."""
    account_client.put(
        VISIBILITY, json={"discoverable": True, "show_location": False}, headers=ana.headers
    )

    assert "city" not in _read(account_client, company, ana.profile_id).json()


# ----------------------------------------------------------------------- roles
def test_a_candidate_cannot_read_another_projection(
    account_client: TestClient, ana: Account
) -> None:
    """The projection is for companies: a candidate gets ``403``."""
    assert _read(account_client, ana, ana.profile_id).status_code == 403


def test_an_anonymous_caller_cannot_read_a_projection(
    account_client: TestClient, ana: Account
) -> None:
    """No token, no projection."""
    assert account_client.get(f"/api/v1/candidates/{ana.profile_id}").status_code == 401


def test_an_invalid_id_is_refused(account_client: TestClient, company: Account) -> None:
    """Path ids are bounded and must be positive."""
    assert account_client.get("/api/v1/candidates/0", headers=company.headers).status_code == 422


# ------------------------------------------------------------------------ logs
def test_the_projection_is_never_logged(
    account_client: TestClient, ana: Account, company: Account, caplog: pytest.LogCaptureFixture
) -> None:
    """Reading a projection writes no personal data to the logs."""
    with caplog.at_level(logging.DEBUG, logger="skillmatch"):
        assert _read(account_client, company, ana.profile_id).status_code == 200

    for record in caplog.records:
        line = JsonFormatter().format(record)
        _assert_no_blocked_field(json.loads(line), "a log line")
        assert "Ana P." not in line
        assert "Backend junior" not in line


def test_sensitive_extra_fields_are_redacted() -> None:
    """A field in :data:`SENSITIVE_KEYS` never reaches the line, even by mistake."""
    record = logging.LogRecord(
        name="skillmatch.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="profile read",
        args=(),
        exc_info=None,
    )
    record.email = "ana@example.test"
    record.display_name = "Ana P."

    line = json.loads(JsonFormatter().format(record))

    assert line["email"] == "[redacted]"
    assert line["display_name"] == "[redacted]"
    assert "Ana P." not in json.dumps(line)
    assert all(key in SENSITIVE_KEYS for key in ("email", "display_name"))
