"""Direct service tests using an isolated SQLite database."""

import asyncio
from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from skillmatch.core.errors import NotFoundError
from skillmatch.modules.candidates.errors import (
    CandidateProfileAlreadyExistsError,
    CandidateProfileNotFoundError,
    SkillAlreadyDeclaredError,
    SkillLimitReachedError,
)
from skillmatch.modules.candidates.models import (
    CandidateProfile,
    CandidateSkill,
    ContractType,
    SkillLevel,
    WorkMode,
)
from skillmatch.modules.candidates.schemas import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    PreferencesUpdate,
    SkillCreate,
    SkillUpdate,
    VisibilityUpdate,
)
from skillmatch.modules.candidates.service import CandidateService
from skillmatch.modules.identity.models import (
    ACTIVE_ACCOUNT_STATUS,
    User,
    UserRole,
)


def run_with_session(
    account_db: async_sessionmaker[AsyncSession],
    scenario: Callable[[AsyncSession], Awaitable[None]],
) -> None:
    """Run an asynchronous scenario with an isolated database session."""

    async def run() -> None:
        async with account_db() as session:
            return await scenario(session)

    return asyncio.run(run())


async def create_candidate(
    session: AsyncSession,
) -> tuple[User, CandidateService, CandidateProfile]:
    """Create a real talent account and its candidate profile."""
    user = User(
        email="candidate@example.test",
        role=UserRole.TALENTO,
        status=ACTIVE_ACCOUNT_STATUS,
        password_hash=None,
    )
    session.add(user)
    await session.commit()

    service = CandidateService(session)
    profile = await service.create_profile(
        user.id,
        CandidateProfileCreate(display_name="Candidate"),
    )
    return user, service, profile


def test_create_profile_rejects_existing_profile(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)

        with pytest.raises(CandidateProfileAlreadyExistsError):
            await service.create_profile(
                user.id,
                CandidateProfileCreate(display_name="Another profile"),
            )

    run_with_session(account_db, scenario)


def test_get_profile_rejects_missing_profile(account_db: async_sessionmaker[AsyncSession]) -> None:
    async def scenario(session: AsyncSession) -> None:
        service = CandidateService(session)

        with pytest.raises(CandidateProfileNotFoundError):
            await service.get_profile(999)

    run_with_session(account_db, scenario)


def test_update_profile_changes_only_supplied_fields(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, profile = await create_candidate(session)

        updated = await service.update_profile(
            user.id,
            CandidateProfileUpdate(summary="New summary", city="Berlin"),
        )

        assert updated.id == profile.id
        assert updated.summary == "New summary"
        assert updated.city == "Berlin"
        assert updated.display_name == "Candidate"

    run_with_session(account_db, scenario)


def test_replace_preferences_persists_all_preference_fields(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)

        updated = await service.replace_preferences(
            user.id,
            PreferencesUpdate(
                work_modes=[WorkMode.REMOTE, WorkMode.HYBRID],
                contract_types=[ContractType.FULL_TIME, ContractType.FREELANCE],
                preferred_locations=["Berlin", "Hamburg"],
                interests=["Data", "Backend"],
            ),
        )

        assert updated.work_modes == ["remote", "hybrid"]
        assert updated.contract_types == ["full_time", "freelance"]
        assert updated.preferred_locations == ["Berlin", "Hamburg"]
        assert updated.interests == ["Data", "Backend"]

    run_with_session(account_db, scenario)


def test_replace_visibility_persists_both_flags(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)

        updated = await service.replace_visibility(
            user.id,
            VisibilityUpdate(discoverable=True, show_location=True),
        )

        assert updated.discoverable is True
        assert updated.show_location is True

    run_with_session(account_db, scenario)


def test_add_skill_rejects_missing_profile(account_db: async_sessionmaker[AsyncSession]) -> None:
    async def scenario(session: AsyncSession) -> None:
        service = CandidateService(session)

        with pytest.raises(CandidateProfileNotFoundError):
            await service.add_skill(
                999,
                SkillCreate(name="Python", level=SkillLevel.ADVANCED),
            )

    run_with_session(account_db, scenario)


def test_add_skill_rejects_profile_at_skill_limit(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        _, service, profile = await create_candidate(session)

        session.add_all(
            [
                CandidateSkill(
                    candidate_id=profile.id,
                    name=f"Skill {number}",
                    name_key=f"skill {number}",
                    level="beginner",
                )
                for number in range(50)
            ]
        )
        await session.flush()

        with pytest.raises(SkillLimitReachedError):
            await service.add_skill(
                profile.user_id,
                SkillCreate(name="Extra skill", level=SkillLevel.BEGINNER),
            )

    run_with_session(account_db, scenario)


def test_add_skill_rejects_duplicate_name_case_insensitively(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)

        await service.add_skill(
            user.id,
            SkillCreate(name="Python", level=SkillLevel.ADVANCED),
        )

        with pytest.raises(SkillAlreadyDeclaredError):
            await service.add_skill(
                user.id,
                SkillCreate(name="PYTHON", level=SkillLevel.BEGINNER),
            )

    run_with_session(account_db, scenario)


def test_get_skill_owner_id_returns_owner_and_rejects_missing_skill(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _profile = await create_candidate(session)
        skill = await service.add_skill(
            user.id,
            SkillCreate(name="Python", level=SkillLevel.ADVANCED),
        )

        assert await service.get_skill_owner_id(skill.id) == user.id

        with pytest.raises(NotFoundError):
            await service.get_skill_owner_id(999)

    run_with_session(account_db, scenario)


def test_update_skill_supports_name_only_and_level_only(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)
        skill = await service.add_skill(
            user.id,
            SkillCreate(name="Python", level=SkillLevel.BEGINNER),
        )

        renamed = await service.update_skill(
            skill.id,
            user.id,
            SkillUpdate(name="Rust"),
        )
        assert renamed.name == "Rust"
        assert renamed.name_key == "rust"
        assert renamed.level == "beginner"

        upgraded = await service.update_skill(
            skill.id,
            user.id,
            SkillUpdate(level=SkillLevel.ADVANCED),
        )
        assert upgraded.name == "Rust"
        assert upgraded.level == "advanced"

    run_with_session(account_db, scenario)


def test_update_skill_rejects_duplicate_name(account_db: async_sessionmaker[AsyncSession]) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)
        first = await service.add_skill(
            user.id,
            SkillCreate(name="Python", level=SkillLevel.ADVANCED),
        )
        await service.add_skill(
            user.id,
            SkillCreate(name="Rust", level=SkillLevel.INTERMEDIATE),
        )

        with pytest.raises(SkillAlreadyDeclaredError):
            await service.update_skill(
                first.id,
                user.id,
                SkillUpdate(name="Rust"),
            )

    run_with_session(account_db, scenario)


def test_update_skill_rejects_skill_owned_by_another_user(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)

        other_user = User(
            email="other@example.test",
            role=UserRole.TALENTO,
            status=ACTIVE_ACCOUNT_STATUS,
            password_hash=None,
        )
        session.add(other_user)
        await session.commit()

        _, _, other_profile = await create_candidate_for_existing_user(session, other_user)
        other_skill = CandidateSkill(
            candidate_id=other_profile.id,
            name="Python",
            name_key="python",
            level="advanced",
        )
        session.add(other_skill)
        await session.commit()
        await session.refresh(other_skill)

        with pytest.raises(NotFoundError):
            await service.update_skill(
                other_skill.id,
                user.id,
                SkillUpdate(level=SkillLevel.BEGINNER),
            )

    run_with_session(account_db, scenario)


async def create_candidate_for_existing_user(
    session: AsyncSession, user: User
) -> tuple[User, CandidateService, CandidateProfile]:
    """Create a profile for an account already stored in the database."""
    service = CandidateService(session)
    profile = await service.create_profile(
        user.id,
        CandidateProfileCreate(display_name="Other candidate"),
    )
    return user, service, profile


def test_delete_skill_removes_owned_skill(account_db: async_sessionmaker[AsyncSession]) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)
        skill = await service.add_skill(
            user.id,
            SkillCreate(name="Python", level=SkillLevel.ADVANCED),
        )

        await service.delete_skill(skill.id, user.id)

        with pytest.raises(NotFoundError):
            await service.update_skill(
                skill.id,
                user.id,
                SkillUpdate(level=SkillLevel.BEGINNER),
            )

    run_with_session(account_db, scenario)


def test_delete_skill_rejects_missing_or_foreign_skill(
    account_db: async_sessionmaker[AsyncSession],
) -> None:
    async def scenario(session: AsyncSession) -> None:
        user, service, _ = await create_candidate(session)

        with pytest.raises(NotFoundError):
            await service.delete_skill(999, user.id)

    run_with_session(account_db, scenario)
