"""Lost uniqueness races in the candidate service (B-03).

Two concurrent requests can both pass the "does it exist?" pre-check and then collide on the
database's unique constraint. The pre-check is blinded here so the service has to rely on that
constraint, which must turn into the same ``409`` the sequential case produces instead of a 500.
"""

import asyncio
from collections.abc import Awaitable, Callable
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from skillmatch.modules.candidates.errors import (
    CandidateProfileAlreadyExistsError,
    SkillAlreadyDeclaredError,
)
from skillmatch.modules.candidates.models import SkillLevel
from skillmatch.modules.candidates.repository import CandidateRepository
from skillmatch.modules.candidates.schemas import (
    CandidateProfileCreate,
    SkillCreate,
    SkillUpdate,
)
from skillmatch.modules.candidates.service import (
    CandidateService,
    _is_profile_user_unique_violation,
    _is_skill_name_unique_violation,
)
from skillmatch.modules.identity.models import User, UserRole


class _PostgresOriginalError(Exception):
    """Simulate PostgreSQL driver errors exposing constraint metadata."""

    def __init__(
        self,
        constraint_name: str | None = None,
        diag: object | None = None,
    ) -> None:
        super().__init__("PostgreSQL integrity constraint violation")
        self.constraint_name = constraint_name
        self.diag = diag


async def _no_profile(_self: CandidateRepository, _user_id: int) -> None:
    """Pretend that the profile does not exist yet."""


async def _name_is_free(
    _self: CandidateRepository,
    _profile_id: int,
    _name_key: str,
    *,
    excluding_skill_id: int | None = None,
) -> bool:
    """Pretend that the skill name is still free."""
    del excluding_skill_id
    return False


async def _service_with_profile(session: AsyncSession) -> tuple[CandidateService, int]:
    """Create a candidate account with a profile and return its service and user id."""
    user = User(email="race@skillmatch.test", role=UserRole.TALENTO, status="active")
    session.add(user)
    await session.commit()
    service = CandidateService(session)
    await service.create_profile(user.id, CandidateProfileCreate(display_name="Race"))
    return service, user.id


def _run(
    factory: async_sessionmaker[AsyncSession],
    scenario: Callable[[AsyncSession], Awaitable[None]],
) -> None:
    async def _main() -> None:
        async with factory() as session:
            await scenario(session)

    asyncio.run(_main())


def test_a_lost_race_creating_the_profile_is_a_conflict(
    account_db: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def scenario(session: AsyncSession) -> None:
        service, user_id = await _service_with_profile(session)
        monkeypatch.setattr(CandidateRepository, "get_profile_by_user", _no_profile)

        with pytest.raises(CandidateProfileAlreadyExistsError):
            await service.create_profile(user_id, CandidateProfileCreate(display_name="Second"))

    _run(account_db, scenario)


def test_a_lost_race_declaring_a_skill_is_a_conflict(
    account_db: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def scenario(session: AsyncSession) -> None:
        service, user_id = await _service_with_profile(session)
        await service.add_skill(user_id, SkillCreate(name="Python", level=SkillLevel.BEGINNER))
        monkeypatch.setattr(CandidateRepository, "skill_name_exists", _name_is_free)

        with pytest.raises(SkillAlreadyDeclaredError):
            await service.add_skill(user_id, SkillCreate(name="python", level=SkillLevel.ADVANCED))

    _run(account_db, scenario)


def test_a_lost_race_renaming_a_skill_is_a_conflict(
    account_db: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def scenario(session: AsyncSession) -> None:
        service, user_id = await _service_with_profile(session)
        await service.add_skill(user_id, SkillCreate(name="Python", level=SkillLevel.BEGINNER))
        sql = await service.add_skill(user_id, SkillCreate(name="SQL", level=SkillLevel.BEGINNER))
        monkeypatch.setattr(CandidateRepository, "skill_name_exists", _name_is_free)

        with pytest.raises(SkillAlreadyDeclaredError):
            await service.update_skill(sql.id, user_id, SkillUpdate(name="PYTHON"))

    _run(account_db, scenario)


def test_non_duplicate_integrity_errors_are_not_mapped_to_skill_conflicts(
    account_db: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sqlalchemy.exc import IntegrityError

    async def scenario(session: AsyncSession) -> None:
        service, user_id = await _service_with_profile(session)

        original_error = IntegrityError(
            "INSERT INTO candidate_skills ...",
            {},
            Exception("foreign key constraint failed"),
        )

        async def fail_commit() -> None:
            raise original_error

        monkeypatch.setattr(session, "commit", fail_commit)

        with pytest.raises(IntegrityError) as captured:
            await service.add_skill(
                user_id,
                SkillCreate(name="Python", level=SkillLevel.BEGINNER),
            )

        assert captured.value is original_error

    _run(account_db, scenario)


def test_non_duplicate_integrity_errors_are_not_mapped_to_profile_conflicts(
    account_db: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sqlalchemy.exc import IntegrityError

    async def scenario(session: AsyncSession) -> None:
        user = User(
            email="profile-integrity@skillmatch.test",
            role=UserRole.TALENTO,
            status="active",
        )
        session.add(user)
        await session.commit()

        service = CandidateService(session)

        original_error = IntegrityError(
            "INSERT INTO candidate_profiles ...",
            {},
            Exception("foreign key constraint failed"),
        )

        rollback_calls = 0
        original_rollback = session.rollback

        async def fail_commit() -> None:
            raise original_error

        async def track_rollback() -> None:
            nonlocal rollback_calls
            rollback_calls += 1
            await original_rollback()

        monkeypatch.setattr(session, "commit", fail_commit)
        monkeypatch.setattr(session, "rollback", track_rollback)

        with pytest.raises(IntegrityError) as captured:
            await service.create_profile(
                user.id,
                CandidateProfileCreate(display_name="Integrity test"),
            )

        assert captured.value is original_error
        assert rollback_calls == 1

    _run(account_db, scenario)


@pytest.mark.parametrize(
    ("detector", "constraint_name", "expected"),
    [
        (_is_profile_user_unique_violation, "ix_candidate_profiles_user_id", True),
        (_is_profile_user_unique_violation, "some_other_constraint", False),
        (
            _is_skill_name_unique_violation,
            "uq_candidate_skills_candidate_id_name_key",
            True,
        ),
        (_is_skill_name_unique_violation, "some_other_constraint", False),
    ],
)
def test_postgresql_constraint_detection(
    detector: Callable[[IntegrityError], bool],
    constraint_name: str,
    expected: bool,
) -> None:
    original = _PostgresOriginalError(constraint_name=constraint_name)
    error = IntegrityError("INSERT statement", {}, original)

    assert detector(error) is expected


@pytest.mark.parametrize(
    ("detector", "constraint_name", "expected"),
    [
        (_is_profile_user_unique_violation, "ix_candidate_profiles_user_id", True),
        (_is_profile_user_unique_violation, "some_other_constraint", False),
        (
            _is_skill_name_unique_violation,
            "uq_candidate_skills_candidate_id_name_key",
            True,
        ),
        (_is_skill_name_unique_violation, "some_other_constraint", False),
    ],
)
def test_postgresql_diag_constraint_detection(
    detector: Callable[[IntegrityError], bool],
    constraint_name: str,
    expected: bool,
) -> None:
    original = _PostgresOriginalError(diag=SimpleNamespace(constraint_name=constraint_name))
    error = IntegrityError("INSERT statement", {}, original)

    assert detector(error) is expected


@pytest.mark.parametrize(
    ("detector", "message", "expected"),
    [
        (
            _is_profile_user_unique_violation,
            "UNIQUE constraint failed: candidate_profiles.user_id",
            True,
        ),
        (
            _is_profile_user_unique_violation,
            "UNIQUE constraint failed: candidate_profiles.display_name",
            False,
        ),
        (
            _is_skill_name_unique_violation,
            "UNIQUE constraint failed: candidate_skills.candidate_id, candidate_skills.name_key",
            True,
        ),
        (
            _is_skill_name_unique_violation,
            "UNIQUE constraint failed: candidate_skills.name_key",
            False,
        ),
    ],
)
def test_sqlite_constraint_detection(
    detector: Callable[[IntegrityError], bool],
    message: str,
    expected: bool,
) -> None:
    original = Exception(message)
    original.sqlite_errorname = "SQLITE_CONSTRAINT_UNIQUE"  # type: ignore[attr-defined]
    error = IntegrityError("INSERT statement", {}, original)

    assert detector(error) is expected
