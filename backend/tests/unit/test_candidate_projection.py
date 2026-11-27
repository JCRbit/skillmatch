"""Unit tests of the allowlist itself (B-06, FR-012).

The endpoint tests read the HTTP response; these check the function that builds it, so every
branch of the allowlist is exercised and the answer to "what happens if a field is added to the
model tomorrow" is a failing test instead of a leak.
"""

from datetime import UTC, datetime

import pytest

from skillmatch.modules.candidates.models import CandidateProfile, CandidateSkill
from skillmatch.modules.candidates.projection import (
    ALLOWED_FIELDS,
    BLOCKED_FIELDS,
    ProjectionStage,
    project_profile,
)


def _profile(**overrides: object) -> CandidateProfile:
    """Build an unsaved profile with every field set."""
    values: dict[str, object] = {
        "user_id": 7,
        "display_name": "Ana P.",
        "summary": "Backend junior",
        "city": "Madrid",
        "languages": ["es", "en"],
        "work_modes": ["remote"],
        "contract_types": ["full_time"],
        "preferred_locations": ["Valencia"],
        "interests": ["backend"],
        "discoverable": True,
        "show_location": True,
    }
    values.update(overrides)
    profile = CandidateProfile(**values)
    profile.id = 3
    profile.created_at = datetime.now(UTC)
    profile.updated_at = datetime.now(UTC)
    return profile


def _skill() -> CandidateSkill:
    """Build an unsaved skill."""
    skill = CandidateSkill(candidate_id=3, name="Python", name_key="python", level="intermediate")
    skill.id = 11
    return skill


def test_the_discovery_stage_never_contains_a_blocked_field() -> None:
    """A fully shared profile still answers with allowed fields only."""
    projected = project_profile(
        _profile(),
        [_skill()],
        location_consented=True,
        skills_consented=True,
    )

    assert not set(projected) & BLOCKED_FIELDS
    assert set(projected) <= ALLOWED_FIELDS[ProjectionStage.DISCOVERY]


def test_a_skill_is_projected_without_its_row_id() -> None:
    """The skill id and name key are internal and never leave the service."""
    projected = project_profile(
        _profile(), [_skill()], location_consented=True, skills_consented=True
    )

    assert projected["skills"] == [{"name": "Python", "level": "intermediate"}]


@pytest.mark.parametrize(
    ("field", "overrides"),
    [
        ("summary", {"summary": None}),
        ("languages", {"languages": []}),
        ("city", {"city": None}),
    ],
)
def test_an_empty_field_is_absent_instead_of_null(field: str, overrides: dict[str, object]) -> None:
    """A value the candidate did not fill is absent, never a null the client can tell apart."""
    projected = project_profile(
        _profile(**overrides),
        [],
        location_consented=True,
        skills_consented=True,
    )

    assert field not in projected


def test_the_city_requires_both_the_flag_and_the_consent() -> None:
    """The narrower of the two conditions wins: either one hides the city."""
    profile = _profile()

    assert "city" not in project_profile(profile, [], location_consented=False)
    assert "city" not in project_profile(_profile(show_location=False), [], location_consented=True)
    assert project_profile(profile, [], location_consented=True)["city"] == "Madrid"


def test_the_match_stage_is_declared_but_adds_nothing_yet() -> None:
    """``MATCH`` is in the allowlist so B-07 extends one place, not two."""
    projected = project_profile(
        _profile(),
        [_skill()],
        stage=ProjectionStage.MATCH,
        location_consented=True,
        skills_consented=True,
    )

    assert set(projected) <= ALLOWED_FIELDS[ProjectionStage.MATCH]
    assert "contact" in ALLOWED_FIELDS[ProjectionStage.MATCH]
    assert "contact" not in projected


def test_every_stage_allows_a_pseudonym_and_nothing_of_the_account() -> None:
    """The pseudonym is the only identifying value any stage may contain."""
    for stage in ProjectionStage:
        assert "display_name" in ALLOWED_FIELDS[stage]
        assert not ALLOWED_FIELDS[stage] & {"user_id", "email", "role", "password_hash"}
