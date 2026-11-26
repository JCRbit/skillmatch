from typing import cast

from sqlalchemy import CheckConstraint, ForeignKey, Table, UniqueConstraint

from skillmatch.modules.candidates.models import (
    CandidateProfile,
    CandidateSkill,
    ContractType,
    SkillLevel,
    WorkMode,
)
from skillmatch.modules.identity.models import User

IDENTITY_COLUMNS = {"email", "password_hash", "role", "status", "last_login_at"}


def test_enum_values_are_the_public_vocabulary() -> None:
    assert [mode.value for mode in WorkMode] == ["remote", "hybrid", "onsite"]
    assert [kind.value for kind in ContractType] == [
        "full_time",
        "part_time",
        "internship",
        "freelance",
    ]
    assert [level.value for level in SkillLevel] == ["beginner", "intermediate", "advanced"]


def test_the_profile_is_linked_to_the_user_only_through_a_unique_foreign_key() -> None:
    columns = CandidateProfile.__table__.columns

    assert columns["user_id"].unique
    assert columns["user_id"].nullable is False
    (foreign_key,) = columns["user_id"].foreign_keys
    assert foreign_key.target_fullname == "users.id"
    assert foreign_key.ondelete == "CASCADE"


def test_identity_data_is_not_duplicated_in_the_profile() -> None:
    profile_columns = set(CandidateProfile.__table__.columns.keys())
    user_columns = set(User.__table__.columns.keys())

    assert not IDENTITY_COLUMNS & profile_columns
    assert user_columns >= IDENTITY_COLUMNS
    assert not {"display_name", "summary", "city", "languages"} & user_columns


def test_a_new_profile_is_private_by_default() -> None:
    columns = CandidateProfile.__table__.columns

    for name in ("discoverable", "show_location"):
        assert columns[name].nullable is False
        assert columns[name].default.arg is False
        assert columns[name].server_default is not None


def test_skills_belong_to_a_profile_and_are_unique_per_profile() -> None:
    table = cast(Table, CandidateSkill.__table__)
    (foreign_key,) = table.columns["candidate_id"].foreign_keys
    unique = [c for c in table.constraints if isinstance(c, UniqueConstraint)]

    assert isinstance(foreign_key, ForeignKey)
    assert foreign_key.target_fullname == "candidate_profiles.id"
    assert foreign_key.ondelete == "CASCADE"
    assert [(c.name, [col.name for col in c.columns]) for c in unique] == [
        ("uq_candidate_skills_candidate_id_name_key", ["candidate_id", "name_key"])
    ]


def test_the_skill_level_check_lists_every_level() -> None:
    table = cast(Table, CandidateSkill.__table__)
    (check,) = [c for c in table.constraints if isinstance(c, CheckConstraint)]

    assert check.name == "ck_candidate_skills_level"
    for level in SkillLevel:
        assert f"'{level.value}'" in str(check.sqltext)
