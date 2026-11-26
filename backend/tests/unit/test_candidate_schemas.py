from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import BaseModel, ValidationError

from skillmatch.modules.candidates.models import SkillLevel
from skillmatch.modules.candidates.schemas import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    PreferencesUpdate,
    SkillCreate,
    SkillName,
    SkillUpdate,
    UtcDatetime,
    VisibilityUpdate,
)


class _Name(BaseModel):
    value: SkillName


class _When(BaseModel):
    value: UtcDatetime


VALID_PREFERENCES: dict[str, list[str]] = {
    "work_modes": [],
    "contract_types": [],
    "preferred_locations": [],
    "interests": [],
}


@pytest.mark.parametrize(
    "name", ["Python", "C++", "C#", ".NET", "CI/CD", "Node.js", "R&D", "ML_Ops"]
)
def test_skill_names_used_in_practice_are_valid(name: str) -> None:
    assert _Name(value=name).value == name


@pytest.mark.parametrize("name", [".", "..", "-x", "+", "a<b", "a;b", "a\nb\u0000", "x" * 61, ""])
def test_skill_names_that_are_not_names_are_invalid(name: str) -> None:
    with pytest.raises(ValidationError):
        _Name(value=name)


def test_whitespace_in_a_skill_name_is_collapsed() -> None:
    assert _Name(value="  Machine \t\n Learning ").value == "Machine Learning"


def test_naive_timestamps_are_read_as_utc() -> None:
    value = _When(value=datetime(2026, 11, 24, 9, 30)).value  # noqa: DTZ001

    assert value == datetime(2026, 11, 24, 9, 30, tzinfo=UTC)
    assert value.utcoffset() == timedelta(0)


def test_aware_timestamps_are_converted_to_utc() -> None:
    plus_two = datetime(2026, 11, 24, 11, 30, tzinfo=timezone(timedelta(hours=2)))

    value = _When(value=plus_two).value

    assert value == datetime(2026, 11, 24, 9, 30, tzinfo=UTC)
    assert value.utcoffset() == timedelta(0)


def test_a_profile_update_must_change_something() -> None:
    with pytest.raises(ValidationError):
        CandidateProfileUpdate()


def test_a_profile_update_only_reports_the_fields_that_were_sent() -> None:
    update = CandidateProfileUpdate(city=None)

    assert update.model_dump(exclude_unset=True) == {"city": None}


def test_a_profile_update_cannot_null_the_display_name_or_languages() -> None:
    with pytest.raises(ValidationError):
        CandidateProfileUpdate(display_name=None)
    with pytest.raises(ValidationError):
        CandidateProfileUpdate(languages=None)


def test_unknown_fields_are_forbidden_in_every_request_model() -> None:
    bodies: list[tuple[type[BaseModel], dict[str, object]]] = [
        (CandidateProfileCreate, {"display_name": "Ana", "user_id": 1}),
        (CandidateProfileUpdate, {"city": "Madrid", "user_id": 1}),
        (PreferencesUpdate, {**VALID_PREFERENCES, "user_id": 1}),
        (VisibilityUpdate, {"discoverable": True, "show_location": True, "user_id": 1}),
        (SkillCreate, {"name": "Python", "level": "beginner", "candidate_id": 1}),
        (SkillUpdate, {"level": "beginner", "candidate_id": 1}),
    ]

    for model, body in bodies:
        with pytest.raises(ValidationError):
            model.model_validate(body)


def test_a_skill_update_cannot_contain_null_values() -> None:
    with pytest.raises(ValidationError):
        SkillUpdate(name=None, level=SkillLevel.ADVANCED)


def test_preferences_ignore_case_when_looking_for_duplicates() -> None:
    with pytest.raises(ValidationError):
        PreferencesUpdate.model_validate({**VALID_PREFERENCES, "interests": ["Data", "data"]})


def test_visibility_flags_are_strict_booleans() -> None:
    with pytest.raises(ValidationError):
        VisibilityUpdate.model_validate({"discoverable": "true", "show_location": False})
