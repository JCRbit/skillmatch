"""Candidate profile, preferences, visibility and declared skills (B-03, FR-002, NFR-005).

Everything goes through the public API against an in-memory database: accounts come from
``POST /auth/register``, tokens from ``POST /auth/login``. Direct database access is only used to
check what was really persisted and to prepare what the API refuses to create (administrators).
"""

import asyncio
from collections.abc import Callable
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from skillmatch.core.security import create_service_token
from skillmatch.modules.candidates.models import CandidateProfile, CandidateSkill
from skillmatch.modules.candidates.service import MAX_SKILLS_PER_CANDIDATE
from skillmatch.modules.identity.models import User, UserRole
from tests.api.conftest import ACCOUNT_SECRET, UserStore

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"
PROFILE = "/api/v1/candidates/me"
PREFERENCES = f"{PROFILE}/preferences"
VISIBILITY = f"{PROFILE}/visibility"
SKILLS = f"{PROFILE}/skills"

PASSWORD = "correct horse battery staple"  # noqa: S105 - synthetic fixture value
ANA = "ana@skillmatch.test"
BEA = "bea@skillmatch.test"
COMPANY = "hr@skillmatch.test"
ADMIN = "admin@skillmatch.test"

Headers = dict[str, str]
Account = Callable[[str], Headers]

PROFILE_BODY: dict[str, Any] = {
    "display_name": "Ana Dev",
    "summary": "Junior backend developer.",
    "city": "Madrid",
    "languages": ["es", "en"],
}
PREFERENCES_BODY: dict[str, Any] = {
    "work_modes": ["remote", "hybrid"],
    "contract_types": ["full_time", "internship"],
    "preferred_locations": ["Madrid", "Valencia"],
    "interests": ["backend", "data"],
}


# --------------------------------------------------------------------------- helpers
def assert_problem(response: Response, *, status: int, code: str) -> dict[str, Any]:
    """Assert an RFC 9457 problem-details response and return its body."""
    body: dict[str, Any] = response.json()
    assert response.status_code == status, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["status"] == status
    assert body["code"] == code
    return body


def _bearer(token: str) -> Headers:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def account(account_client: TestClient, user_store: UserStore) -> Account:
    """Return a function that registers (once) and signs in an account of the given email.

    The role is derived from the email: ``hr@`` is a company, ``admin@`` an administrator
    (inserted directly, because the API refuses to create one) and anything else a candidate.
    """

    def _account(email: str) -> Headers:
        if email == ADMIN:
            if user_store.get(email) is None:
                user_store.add(email=email, role=UserRole.ADMIN, password_hash=None)
            stored = user_store.get(email)
            assert stored is not None
            token = create_service_token(
                subject=str(stored.id), role="admin", secret=ACCOUNT_SECRET, expires_in=600
            )
            return _bearer(token)
        role = "empresa" if email == COMPANY else "talento"
        if user_store.get(email) is None:
            created = account_client.post(
                REGISTER, json={"email": email, "password": PASSWORD, "role": role}
            )
            assert created.status_code == 201, created.text
        login = account_client.post(LOGIN, json={"email": email, "password": PASSWORD})
        assert login.status_code == 200, login.text
        return _bearer(login.json()["access_token"])

    return _account


@pytest.fixture
def ana(account: Account) -> Headers:
    """Headers of a signed-in candidate."""
    return account(ANA)


@pytest.fixture
def bea(account: Account) -> Headers:
    """Headers of a second, unrelated candidate."""
    return account(BEA)


def create_profile(
    client: TestClient, headers: Headers, body: dict[str, Any] | None = None
) -> Response:
    """Create a profile, defaulting to :data:`PROFILE_BODY`."""
    return client.post(PROFILE, json=PROFILE_BODY if body is None else body, headers=headers)


def add_skill(client: TestClient, headers: Headers, name: str, level: str = "beginner") -> Response:
    """Declare one skill."""
    return client.post(SKILLS, json={"name": name, "level": level}, headers=headers)


def stored_profile(
    factory: async_sessionmaker[AsyncSession], email: str
) -> CandidateProfile | None:
    """Read the profile of an account straight from the database."""

    async def _read() -> CandidateProfile | None:
        async with factory() as session:
            result = await session.execute(
                select(CandidateProfile)
                .join(User, User.id == CandidateProfile.user_id)
                .where(User.email == email)
            )
            return result.scalar_one_or_none()

    return asyncio.run(_read())


def stored_skills(factory: async_sessionmaker[AsyncSession], email: str) -> list[CandidateSkill]:
    """Read the skills of an account straight from the database."""

    async def _read() -> list[CandidateSkill]:
        async with factory() as session:
            result = await session.execute(
                select(CandidateSkill)
                .join(CandidateProfile, CandidateProfile.id == CandidateSkill.candidate_id)
                .join(User, User.id == CandidateProfile.user_id)
                .where(User.email == email)
                .order_by(CandidateSkill.id)
            )
            return list(result.scalars().all())

    return asyncio.run(_read())


def count_rows(factory: async_sessionmaker[AsyncSession], model: type[Any]) -> int:
    """Count the rows of a table."""

    async def _count() -> int:
        async with factory() as session:
            result = await session.execute(select(func.count()).select_from(model))
            return int(result.scalar_one())

    return asyncio.run(_count())


# ---------------------------------------------------------------- authentication / roles
ENDPOINTS: list[tuple[str, str, dict[str, Any] | None]] = [
    ("POST", PROFILE, PROFILE_BODY),
    ("GET", PROFILE, None),
    ("PATCH", PROFILE, {"city": "Sevilla"}),
    ("DELETE", PROFILE, None),
    ("PUT", PREFERENCES, PREFERENCES_BODY),
    ("PUT", VISIBILITY, {"discoverable": True, "show_location": False}),
    ("GET", SKILLS, None),
    ("POST", SKILLS, {"name": "Python", "level": "beginner"}),
    ("PATCH", f"{SKILLS}/1", {"level": "advanced"}),
    ("DELETE", f"{SKILLS}/1", None),
]
ENDPOINT_IDS = [f"{method} {path.removeprefix(PROFILE) or '/me'}" for method, path, _ in ENDPOINTS]


@pytest.mark.parametrize(("method", "path", "body"), ENDPOINTS, ids=ENDPOINT_IDS)
def test_every_endpoint_requires_authentication(
    account_client: TestClient, method: str, path: str, body: dict[str, Any] | None
) -> None:
    response = account_client.request(method, path, json=body)

    assert_problem(response, status=401, code="authentication_required")


@pytest.mark.parametrize(("method", "path", "body"), ENDPOINTS, ids=ENDPOINT_IDS)
def test_a_forged_token_is_rejected_on_every_endpoint(
    account_client: TestClient, method: str, path: str, body: dict[str, Any] | None
) -> None:
    forged = create_service_token(
        subject="1",
        role="talento",
        secret="a-different-secret",  # noqa: S106 - wrong key on purpose
    )

    response = account_client.request(method, path, json=body, headers=_bearer(forged))

    assert_problem(response, status=401, code="invalid_credentials")


@pytest.mark.parametrize("email", [COMPANY, ADMIN], ids=["company", "admin"])
@pytest.mark.parametrize(("method", "path", "body"), ENDPOINTS, ids=ENDPOINT_IDS)
def test_only_candidates_reach_the_candidate_endpoints(
    account_client: TestClient,
    account: Account,
    email: str,
    method: str,
    path: str,
    body: dict[str, Any] | None,
) -> None:
    response = account_client.request(method, path, json=body, headers=account(email))

    assert_problem(response, status=403, code="permission_denied")


def test_a_suspended_candidate_cannot_use_an_existing_token(
    account_client: TestClient, user_store: UserStore, ana: Headers
) -> None:
    assert create_profile(account_client, ana).status_code == 201
    user_store.set_status(ANA, "suspended")

    response = account_client.get(PROFILE, headers=ana)

    assert_problem(response, status=401, code="invalid_credentials")


# --------------------------------------------------------------------- create and read
def test_a_candidate_can_create_and_read_their_profile(
    account_client: TestClient, ana: Headers
) -> None:
    created = create_profile(account_client, ana)

    assert created.status_code == 201, created.text
    read = account_client.get(PROFILE, headers=ana)
    assert read.status_code == 200
    assert read.json() == created.json()
    body = read.json()
    assert body["display_name"] == "Ana Dev"
    assert body["summary"] == "Junior backend developer."
    assert body["city"] == "Madrid"
    assert body["languages"] == ["es", "en"]


def test_a_new_profile_is_private_and_has_no_preferences(
    account_client: TestClient, ana: Headers
) -> None:
    body = create_profile(account_client, ana).json()

    assert body["visibility"] == {"discoverable": False, "show_location": False}
    assert body["preferences"] == {
        "work_modes": [],
        "contract_types": [],
        "preferred_locations": [],
        "interests": [],
    }


def test_the_profile_never_exposes_identity_data(account_client: TestClient, ana: Headers) -> None:
    body = create_profile(account_client, ana).json()

    assert set(body) == {
        "display_name",
        "summary",
        "city",
        "languages",
        "preferences",
        "visibility",
        "created_at",
        "updated_at",
    }
    assert ANA not in str(body)


def test_optional_fields_can_be_omitted(account_client: TestClient, ana: Headers) -> None:
    response = create_profile(account_client, ana, {"display_name": "Pseudonym"})

    assert response.status_code == 201
    body = response.json()
    assert (body["summary"], body["city"], body["languages"]) == (None, None, [])


def test_text_is_normalised_on_input(account_client: TestClient, ana: Headers) -> None:
    body = create_profile(
        account_client,
        ana,
        {"display_name": "  Ana    Dev  ", "city": " Santa   Cruz ", "languages": [" ES ", "En"]},
    ).json()

    assert body["display_name"] == "Ana Dev"
    assert body["city"] == "Santa Cruz"
    assert body["languages"] == ["es", "en"]


def test_timestamps_are_timezone_aware(account_client: TestClient, ana: Headers) -> None:
    body = create_profile(account_client, ana).json()

    assert body["created_at"].endswith(("Z", "+00:00"))
    assert body["updated_at"].endswith(("Z", "+00:00"))


def test_reading_before_creating_answers_404(account_client: TestClient, ana: Headers) -> None:
    response = account_client.get(PROFILE, headers=ana)

    assert_problem(response, status=404, code="candidate_profile_not_found")


def test_a_candidate_cannot_create_a_second_profile(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)

    response = create_profile(account_client, ana, {"display_name": "Another"})

    assert_problem(response, status=409, code="candidate_profile_already_exists")
    assert account_client.get(PROFILE, headers=ana).json()["display_name"] == "Ana Dev"


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"display_name": ""},
        {"display_name": "   "},
        {"display_name": "x" * 81},
        {"display_name": None},
        {"display_name": "Ana", "summary": "x" * 2001},
        {"display_name": "Ana", "summary": "   "},
        {"display_name": "Ana", "city": "x" * 101},
        {"display_name": "Ana", "languages": ["español"]},
        {"display_name": "Ana", "languages": ["es", "ES"]},
        {"display_name": "Ana", "languages": [letter * 2 for letter in "abcdefghijk"]},
        {"display_name": "Ana", "languages": "es"},
    ],
    ids=[
        "empty-body",
        "empty-name",
        "blank-name",
        "name-too-long",
        "null-name",
        "summary-too-long",
        "blank-summary",
        "city-too-long",
        "bad-language-code",
        "duplicate-language",
        "too-many-languages",
        "languages-not-a-list",
    ],
)
def test_invalid_profiles_are_rejected(
    account_client: TestClient, ana: Headers, body: dict[str, Any]
) -> None:
    response = create_profile(account_client, ana, body)

    assert_problem(response, status=422, code="validation_error")
    assert account_client.get(PROFILE, headers=ana).status_code == 404


def test_validation_errors_do_not_echo_personal_data(
    account_client: TestClient, ana: Headers
) -> None:
    response = create_profile(
        account_client, ana, {"display_name": "Ana", "summary": "secret-" + "x" * 2000}
    )

    assert response.status_code == 422
    assert "secret-" not in response.text


# ------------------------------------------------------------- identity comes from the server
@pytest.mark.parametrize(
    "extra", [{"user_id": 1}, {"id": 1}, {"email": "x@y.test"}, {"role": "admin"}]
)
def test_the_client_cannot_choose_the_owner_of_a_profile(
    account_client: TestClient, ana: Headers, extra: dict[str, Any]
) -> None:
    response = create_profile(account_client, ana, {**PROFILE_BODY, **extra})

    assert_problem(response, status=422, code="validation_error")


def test_a_spoofed_identity_header_is_ignored(
    account_client: TestClient, user_store: UserStore, ana: Headers, bea: Headers
) -> None:
    create_profile(account_client, ana)
    bea_user = user_store.get(BEA)
    assert bea_user is not None

    # Ana's token is presented together with headers that claim to be Bea.
    spoofed = {**ana, "X-User-Id": str(bea_user.id), "X-Candidate-Id": str(bea_user.id)}
    response = account_client.get(PROFILE, headers=spoofed)

    assert response.status_code == 200
    assert response.json()["display_name"] == "Ana Dev"
    assert account_client.get(PROFILE, headers=bea).status_code == 404


# ----------------------------------------------------------------------------- update
def test_a_partial_update_changes_only_the_fields_sent(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)

    response = account_client.patch(PROFILE, json={"city": "Sevilla"}, headers=ana)

    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "Sevilla"
    assert body["display_name"] == "Ana Dev"
    assert body["summary"] == "Junior backend developer."
    assert body["languages"] == ["es", "en"]


def test_a_full_update_replaces_every_profile_field(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)

    response = account_client.patch(
        PROFILE,
        json={"display_name": "AnaD", "summary": "New", "city": "Bilbao", "languages": ["fr"]},
        headers=ana,
    )

    body = response.json()
    assert (body["display_name"], body["summary"], body["city"], body["languages"]) == (
        "AnaD",
        "New",
        "Bilbao",
        ["fr"],
    )


def test_optional_fields_can_be_cleared_with_null(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)

    response = account_client.patch(PROFILE, json={"city": None, "summary": None}, headers=ana)

    body = response.json()
    assert (body["city"], body["summary"]) == (None, None)
    assert body["display_name"] == "Ana Dev"


def test_languages_can_be_cleared_with_an_empty_list(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)

    response = account_client.patch(PROFILE, json={"languages": []}, headers=ana)

    assert response.json()["languages"] == []


@pytest.mark.parametrize(
    "body",
    [{}, {"display_name": None}, {"languages": None}, {"display_name": ""}, {"user_id": 5}],
    ids=["empty", "null-name", "null-languages", "empty-name", "unknown-field"],
)
def test_invalid_updates_are_rejected_and_change_nothing(
    account_client: TestClient, ana: Headers, body: dict[str, Any]
) -> None:
    create_profile(account_client, ana)

    response = account_client.patch(PROFILE, json=body, headers=ana)

    assert_problem(response, status=422, code="validation_error")
    assert account_client.get(PROFILE, headers=ana).json()["display_name"] == "Ana Dev"


def test_updating_before_creating_answers_404(account_client: TestClient, ana: Headers) -> None:
    response = account_client.patch(PROFILE, json={"city": "Sevilla"}, headers=ana)

    assert_problem(response, status=404, code="candidate_profile_not_found")


def test_updating_refreshes_the_modification_time(account_client: TestClient, ana: Headers) -> None:
    created = create_profile(account_client, ana).json()

    updated = account_client.patch(PROFILE, json={"city": "Sevilla"}, headers=ana).json()

    assert updated["created_at"] == created["created_at"]
    assert datetime.fromisoformat(updated["updated_at"]) >= datetime.fromisoformat(
        created["updated_at"]
    )


# --------------------------------------------------------------------------- preferences
def test_preferences_can_be_replaced_and_are_returned_with_the_profile(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)

    response = account_client.put(PREFERENCES, json=PREFERENCES_BODY, headers=ana)

    assert response.status_code == 200
    assert response.json() == PREFERENCES_BODY
    assert account_client.get(PROFILE, headers=ana).json()["preferences"] == PREFERENCES_BODY


def test_replacing_preferences_replaces_all_of_them(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    account_client.put(PREFERENCES, json=PREFERENCES_BODY, headers=ana)
    replacement = {
        "work_modes": ["onsite"],
        "contract_types": [],
        "preferred_locations": [],
        "interests": ["frontend"],
    }

    response = account_client.put(PREFERENCES, json=replacement, headers=ana)

    assert response.json() == replacement


def test_preferences_do_not_touch_the_profile_or_the_visibility(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    account_client.put(VISIBILITY, json={"discoverable": True, "show_location": True}, headers=ana)

    account_client.put(PREFERENCES, json=PREFERENCES_BODY, headers=ana)

    body = account_client.get(PROFILE, headers=ana).json()
    assert body["display_name"] == "Ana Dev"
    assert body["visibility"] == {"discoverable": True, "show_location": True}


@pytest.mark.parametrize(
    "change",
    [
        {"work_modes": ["office"]},
        {"work_modes": ["remote", "remote"]},
        {"contract_types": ["permanent"]},
        {"preferred_locations": ["Madrid", "madrid"]},
        {"preferred_locations": [f"City {number}" for number in range(11)]},
        {"preferred_locations": [""]},
        {"interests": [f"Topic {number}" for number in range(21)]},
        {"interests": ["y" * 61]},
        {"interests": "backend"},
    ],
    ids=[
        "unknown-work-mode",
        "duplicate-work-mode",
        "unknown-contract",
        "duplicate-location",
        "too-many-locations",
        "empty-location",
        "too-many-interests",
        "interest-too-long",
        "interests-not-a-list",
    ],
)
def test_invalid_preferences_are_rejected(
    account_client: TestClient, ana: Headers, change: dict[str, Any]
) -> None:
    create_profile(account_client, ana)

    response = account_client.put(PREFERENCES, json={**PREFERENCES_BODY, **change}, headers=ana)

    assert_problem(response, status=422, code="validation_error")


@pytest.mark.parametrize("missing", list(PREFERENCES_BODY))
def test_omitting_a_preference_cannot_wipe_it(
    account_client: TestClient, ana: Headers, missing: str
) -> None:
    create_profile(account_client, ana)
    account_client.put(PREFERENCES, json=PREFERENCES_BODY, headers=ana)
    partial = {key: value for key, value in PREFERENCES_BODY.items() if key != missing}

    response = account_client.put(PREFERENCES, json=partial, headers=ana)

    assert_problem(response, status=422, code="validation_error")
    assert account_client.get(PROFILE, headers=ana).json()["preferences"] == PREFERENCES_BODY


def test_preferences_need_a_profile(account_client: TestClient, ana: Headers) -> None:
    response = account_client.put(PREFERENCES, json=PREFERENCES_BODY, headers=ana)

    assert_problem(response, status=404, code="candidate_profile_not_found")


# ---------------------------------------------------------------------------- visibility
def test_visibility_flags_can_be_set_and_persist(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)

    response = account_client.put(
        VISIBILITY, json={"discoverable": True, "show_location": False}, headers=ana
    )

    assert response.status_code == 200
    assert response.json() == {"discoverable": True, "show_location": False}
    assert account_client.get(PROFILE, headers=ana).json()["visibility"] == {
        "discoverable": True,
        "show_location": False,
    }


def test_visibility_can_be_withdrawn(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)
    account_client.put(VISIBILITY, json={"discoverable": True, "show_location": True}, headers=ana)

    response = account_client.put(
        VISIBILITY, json={"discoverable": False, "show_location": False}, headers=ana
    )

    assert response.json() == {"discoverable": False, "show_location": False}


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"discoverable": True},
        {"show_location": True},
        {"discoverable": "yes", "show_location": False},
        {"discoverable": 1, "show_location": False},
        {"discoverable": None, "show_location": False},
        {"discoverable": True, "show_location": False, "user_id": 3},
    ],
    ids=[
        "empty",
        "missing-show-location",
        "missing-discoverable",
        "string-instead-of-bool",
        "number-instead-of-bool",
        "null",
        "unknown-field",
    ],
)
def test_visibility_must_be_explicit_and_strictly_boolean(
    account_client: TestClient, ana: Headers, body: dict[str, Any]
) -> None:
    create_profile(account_client, ana)

    response = account_client.put(VISIBILITY, json=body, headers=ana)

    assert_problem(response, status=422, code="validation_error")
    assert account_client.get(PROFILE, headers=ana).json()["visibility"] == {
        "discoverable": False,
        "show_location": False,
    }


def test_visibility_needs_a_profile(account_client: TestClient, ana: Headers) -> None:
    response = account_client.put(
        VISIBILITY, json={"discoverable": True, "show_location": True}, headers=ana
    )

    assert_problem(response, status=404, code="candidate_profile_not_found")


# ------------------------------------------------------------------------------ delete
def test_deleting_the_profile_removes_it_and_its_skills_but_not_the_account(
    account_client: TestClient,
    account_db: async_sessionmaker[AsyncSession],
    user_store: UserStore,
    ana: Headers,
) -> None:
    create_profile(account_client, ana)
    add_skill(account_client, ana, "Python")
    add_skill(account_client, ana, "SQL")

    response = account_client.delete(PROFILE, headers=ana)

    assert response.status_code == 204
    assert response.content == b""
    assert account_client.get(PROFILE, headers=ana).status_code == 404
    assert stored_profile(account_db, ANA) is None
    assert count_rows(account_db, CandidateSkill) == 0
    assert user_store.get(ANA) is not None
    assert account_client.get(ME, headers=ana).status_code == 200


def test_deleting_does_not_affect_another_candidate(
    account_client: TestClient,
    account_db: async_sessionmaker[AsyncSession],
    ana: Headers,
    bea: Headers,
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea"})
    add_skill(account_client, bea, "Python")

    account_client.delete(PROFILE, headers=ana)

    assert account_client.get(PROFILE, headers=bea).json()["display_name"] == "Bea"
    assert [skill.name for skill in stored_skills(account_db, BEA)] == ["Python"]


def test_a_candidate_can_create_a_new_profile_after_deleting(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    account_client.delete(PROFILE, headers=ana)

    response = create_profile(account_client, ana, {"display_name": "Fresh start"})

    assert response.status_code == 201
    assert response.json()["languages"] == []


def test_deleting_without_a_profile_answers_404(account_client: TestClient, ana: Headers) -> None:
    response = account_client.delete(PROFILE, headers=ana)

    assert_problem(response, status=404, code="candidate_profile_not_found")


# ------------------------------------------------------------------------------ skills
def test_a_candidate_can_declare_and_list_skills(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)

    created = add_skill(account_client, ana, "Python", "intermediate")

    assert created.status_code == 201, created.text
    body = created.json()
    assert set(body) == {"id", "name", "level", "created_at", "updated_at"}
    assert (body["name"], body["level"]) == ("Python", "intermediate")
    assert account_client.get(SKILLS, headers=ana).json() == [body]


def test_skills_are_listed_ordered_by_name_ignoring_case(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    for name in ("sql", "Python", "Docker"):
        add_skill(account_client, ana, name)

    names = [skill["name"] for skill in account_client.get(SKILLS, headers=ana).json()]

    assert names == ["Docker", "Python", "sql"]


def test_an_empty_skill_list_is_valid(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)

    response = account_client.get(SKILLS, headers=ana)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("name", ["C++", "C#", ".NET", "CI/CD", "Node.js", "R&D", "SQL (Postgres)"])
def test_real_world_skill_names_are_accepted(
    account_client: TestClient, ana: Headers, name: str
) -> None:
    create_profile(account_client, ana)

    response = add_skill(account_client, ana, name)

    assert response.status_code == 201, response.text
    assert response.json()["name"] == name


def test_skill_names_are_normalised(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)

    response = add_skill(account_client, ana, "  Machine    Learning ")

    assert response.json()["name"] == "Machine Learning"


def test_a_skill_cannot_be_declared_twice_ignoring_case(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    add_skill(account_client, ana, "Python")

    response = add_skill(account_client, ana, "  python ", "advanced")

    assert_problem(response, status=409, code="skill_already_declared")
    assert len(account_client.get(SKILLS, headers=ana).json()) == 1


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"name": "Python"},
        {"level": "beginner"},
        {"name": "", "level": "beginner"},
        {"name": "x" * 61, "level": "beginner"},
        {"name": "<script>alert(1)</script>", "level": "beginner"},
        {"name": "Python\u0000", "level": "beginner"},
        {"name": "-leading-dash", "level": "beginner"},
        {"name": "...", "level": "beginner"},
        {"name": "Python", "level": "expert"},
        {"name": "Python", "level": None},
        {"name": "Python", "level": "beginner", "candidate_id": 1},
    ],
    ids=[
        "empty",
        "missing-level",
        "missing-name",
        "empty-name",
        "name-too-long",
        "markup",
        "control-character",
        "leading-punctuation",
        "punctuation-only",
        "unknown-level",
        "null-level",
        "unknown-field",
    ],
)
def test_invalid_skills_are_rejected(
    account_client: TestClient, ana: Headers, body: dict[str, Any]
) -> None:
    create_profile(account_client, ana)

    response = account_client.post(SKILLS, json=body, headers=ana)

    assert_problem(response, status=422, code="validation_error")
    assert account_client.get(SKILLS, headers=ana).json() == []


def test_skills_need_a_profile(account_client: TestClient, ana: Headers) -> None:
    assert_problem(
        account_client.get(SKILLS, headers=ana), status=404, code="candidate_profile_not_found"
    )
    assert_problem(
        add_skill(account_client, ana, "Python"), status=404, code="candidate_profile_not_found"
    )


def test_a_candidate_cannot_exceed_the_skill_limit(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    for number in range(MAX_SKILLS_PER_CANDIDATE):
        assert add_skill(account_client, ana, f"Skill {number}").status_code == 201

    response = add_skill(account_client, ana, "One too many")

    assert_problem(response, status=409, code="skill_limit_reached")
    assert len(account_client.get(SKILLS, headers=ana).json()) == MAX_SKILLS_PER_CANDIDATE


def test_a_skill_can_be_updated(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)
    skill_id = add_skill(account_client, ana, "Python").json()["id"]

    renamed = account_client.patch(
        f"{SKILLS}/{skill_id}", json={"name": "Python 3", "level": "advanced"}, headers=ana
    )

    assert renamed.status_code == 200, renamed.text
    body = renamed.json()
    assert (body["id"], body["name"], body["level"]) == (skill_id, "Python 3", "advanced")


def test_only_the_level_can_be_updated(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)
    skill_id = add_skill(account_client, ana, "Python").json()["id"]

    response = account_client.patch(f"{SKILLS}/{skill_id}", json={"level": "advanced"}, headers=ana)

    assert (response.json()["name"], response.json()["level"]) == ("Python", "advanced")


def test_a_skill_can_change_only_its_capitalisation(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    skill_id = add_skill(account_client, ana, "python").json()["id"]

    response = account_client.patch(f"{SKILLS}/{skill_id}", json={"name": "Python"}, headers=ana)

    assert response.status_code == 200
    assert response.json()["name"] == "Python"


def test_a_skill_cannot_be_renamed_to_another_declared_skill(
    account_client: TestClient, ana: Headers
) -> None:
    create_profile(account_client, ana)
    add_skill(account_client, ana, "Python")
    sql_id = add_skill(account_client, ana, "SQL").json()["id"]

    response = account_client.patch(f"{SKILLS}/{sql_id}", json={"name": "PYTHON"}, headers=ana)

    assert_problem(response, status=409, code="skill_already_declared")
    names = [skill["name"] for skill in account_client.get(SKILLS, headers=ana).json()]
    assert names == ["Python", "SQL"]


@pytest.mark.parametrize(
    "body",
    [{}, {"name": None}, {"level": None}, {"level": "expert"}, {"name": ""}, {"id": 4}],
    ids=["empty", "null-name", "null-level", "unknown-level", "empty-name", "unknown-field"],
)
def test_invalid_skill_updates_are_rejected(
    account_client: TestClient, ana: Headers, body: dict[str, Any]
) -> None:
    create_profile(account_client, ana)
    skill_id = add_skill(account_client, ana, "Python").json()["id"]

    response = account_client.patch(f"{SKILLS}/{skill_id}", json=body, headers=ana)

    assert_problem(response, status=422, code="validation_error")


@pytest.mark.parametrize("skill_id", ["0", "-1", "abc", "99999999999999999999"])
def test_a_malformed_skill_id_is_a_validation_error(
    account_client: TestClient, ana: Headers, skill_id: str
) -> None:
    create_profile(account_client, ana)

    patched = account_client.patch(f"{SKILLS}/{skill_id}", json={"level": "advanced"}, headers=ana)
    deleted = account_client.delete(f"{SKILLS}/{skill_id}", headers=ana)

    assert_problem(patched, status=422, code="validation_error")
    assert_problem(deleted, status=422, code="validation_error")


def test_a_skill_can_be_deleted(account_client: TestClient, ana: Headers) -> None:
    create_profile(account_client, ana)
    skill_id = add_skill(account_client, ana, "Python").json()["id"]
    add_skill(account_client, ana, "SQL")

    response = account_client.delete(f"{SKILLS}/{skill_id}", headers=ana)

    assert response.status_code == 204
    names = [skill["name"] for skill in account_client.get(SKILLS, headers=ana).json()]
    assert names == ["SQL"]
    assert add_skill(account_client, ana, "Python").status_code == 201


# -------------------------------------------------------------- cross-account isolation
def test_each_candidate_only_ever_sees_their_own_profile(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea", "city": "Lisboa"})

    assert account_client.get(PROFILE, headers=ana).json()["display_name"] == "Ana Dev"
    assert account_client.get(PROFILE, headers=bea).json()["display_name"] == "Bea"


def test_modifying_your_profile_never_changes_someone_elses(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea"})

    account_client.patch(PROFILE, json={"display_name": "Changed"}, headers=bea)
    account_client.put(PREFERENCES, json=PREFERENCES_BODY, headers=bea)
    account_client.put(VISIBILITY, json={"discoverable": True, "show_location": True}, headers=bea)

    body = account_client.get(PROFILE, headers=ana).json()
    assert body["display_name"] == "Ana Dev"
    assert body["preferences"]["work_modes"] == []
    assert body["visibility"] == {"discoverable": False, "show_location": False}


def test_a_candidate_cannot_see_the_skills_of_another(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea"})
    add_skill(account_client, ana, "Python")

    assert account_client.get(SKILLS, headers=bea).json() == []


def test_two_candidates_may_declare_the_same_skill(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea"})

    assert add_skill(account_client, ana, "Python").status_code == 201
    assert add_skill(account_client, bea, "Python").status_code == 201


def test_a_candidate_cannot_update_the_skill_of_another(
    account_client: TestClient,
    account_db: async_sessionmaker[AsyncSession],
    ana: Headers,
    bea: Headers,
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea"})
    ana_skill = add_skill(account_client, ana, "Python", "beginner").json()["id"]

    response = account_client.patch(
        f"{SKILLS}/{ana_skill}", json={"name": "Hacked", "level": "advanced"}, headers=bea
    )

    assert_problem(response, status=404, code="not_found")
    (skill,) = stored_skills(account_db, ANA)
    assert (skill.name, skill.level) == ("Python", "beginner")


def test_a_candidate_cannot_delete_the_skill_of_another(
    account_client: TestClient,
    account_db: async_sessionmaker[AsyncSession],
    ana: Headers,
    bea: Headers,
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea"})
    ana_skill = add_skill(account_client, ana, "Python").json()["id"]

    response = account_client.delete(f"{SKILLS}/{ana_skill}", headers=bea)

    assert_problem(response, status=404, code="not_found")
    assert [skill.name for skill in stored_skills(account_db, ANA)] == ["Python"]


def test_someone_elses_skill_is_indistinguishable_from_a_missing_one(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    create_profile(account_client, ana)
    create_profile(account_client, bea, {"display_name": "Bea"})
    ana_skill = add_skill(account_client, ana, "Python").json()["id"]
    missing = ana_skill + 1000

    foreign = account_client.patch(f"{SKILLS}/{ana_skill}", json={"level": "advanced"}, headers=bea)
    absent = account_client.patch(f"{SKILLS}/{missing}", json={"level": "advanced"}, headers=bea)

    assert foreign.status_code == absent.status_code == 404
    for key in ("title", "code", "detail", "status", "type"):
        assert foreign.json()[key] == absent.json()[key]


def test_a_candidate_without_a_profile_cannot_touch_the_skill_of_another(
    account_client: TestClient, ana: Headers, bea: Headers
) -> None:
    create_profile(account_client, ana)
    ana_skill = add_skill(account_client, ana, "Python").json()["id"]

    response = account_client.delete(f"{SKILLS}/{ana_skill}", headers=bea)

    assert_problem(response, status=404, code="not_found")
    assert len(account_client.get(SKILLS, headers=ana).json()) == 1


# ---------------------------------------------------------------------- persistence
def test_changes_persist_and_stay_linked_to_the_authenticated_account(
    account_client: TestClient,
    account_db: async_sessionmaker[AsyncSession],
    user_store: UserStore,
    ana: Headers,
    bea: Headers,
) -> None:
    create_profile(account_client, ana)
    account_client.patch(PROFILE, json={"city": "Sevilla"}, headers=ana)
    account_client.put(PREFERENCES, json=PREFERENCES_BODY, headers=ana)
    account_client.put(VISIBILITY, json={"discoverable": True, "show_location": False}, headers=ana)
    add_skill(account_client, ana, "Python", "intermediate")

    profile = stored_profile(account_db, ANA)

    assert profile is not None
    ana_user = user_store.get(ANA)
    assert ana_user is not None
    assert profile.user_id == ana_user.id
    assert (profile.display_name, profile.city) == ("Ana Dev", "Sevilla")
    assert profile.languages == ["es", "en"]
    assert profile.work_modes == ["remote", "hybrid"]
    assert profile.contract_types == ["full_time", "internship"]
    assert profile.preferred_locations == ["Madrid", "Valencia"]
    assert profile.interests == ["backend", "data"]
    assert (profile.discoverable, profile.show_location) == (True, False)
    (skill,) = stored_skills(account_db, ANA)
    assert (skill.candidate_id, skill.name, skill.name_key, skill.level) == (
        profile.id,
        "Python",
        "python",
        "intermediate",
    )
    assert stored_profile(account_db, BEA) is None
    assert account_client.get(PROFILE, headers=bea).status_code == 404


def test_the_identity_record_is_not_modified_by_profile_operations(
    account_client: TestClient, user_store: UserStore, ana: Headers
) -> None:
    before = user_store.get(ANA)
    assert before is not None
    snapshot = (before.id, before.email, before.role, before.status, before.password_hash)

    create_profile(account_client, ana)
    account_client.patch(PROFILE, json={"display_name": "Else"}, headers=ana)
    account_client.delete(PROFILE, headers=ana)

    after = user_store.get(ANA)
    assert after is not None
    assert (after.id, after.email, after.role, after.status, after.password_hash) == snapshot


def test_the_database_enforces_the_skill_level_and_uniqueness(
    account_client: TestClient,
    account_db: async_sessionmaker[AsyncSession],
    ana: Headers,
) -> None:
    create_profile(account_client, ana)
    add_skill(account_client, ana, "Python")
    profile = stored_profile(account_db, ANA)
    assert profile is not None

    async def _insert(name: str, name_key: str, level: str) -> None:
        async with account_db() as session:
            session.add(
                CandidateSkill(candidate_id=profile.id, name=name, name_key=name_key, level=level)
            )
            await session.commit()

    with pytest.raises(IntegrityError):
        asyncio.run(_insert("Rust", "rust", "godlike"))
    with pytest.raises(IntegrityError):
        asyncio.run(_insert("PYTHON", "python", "beginner"))
