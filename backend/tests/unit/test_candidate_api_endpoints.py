"""Direct unit tests for the candidate API endpoint functions."""

import asyncio
from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.api.candidates import (
    add_skill,
    create_profile,
    delete_profile,
    delete_skill,
    get_candidate_service,
    list_skills,
    read_profile,
    replace_preferences,
    replace_visibility,
    update_profile,
    update_skill,
)
from skillmatch.core.errors import NotFoundError
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
from skillmatch.modules.identity.models import UserRole

_NOW = datetime(2026, 11, 24, 10, 0, tzinfo=UTC)
_USER = type("TestUser", (), {"id": 7, "role": UserRole.TALENTO})()


def make_profile() -> CandidateProfile:
    return CandidateProfile(
        id=11,
        user_id=_USER.id,
        display_name="Ana",
        summary="Backend developer",
        city="Berlin",
        languages=["es", "en"],
        work_modes=["remote"],
        contract_types=["full_time"],
        preferred_locations=["Berlin"],
        interests=["Data"],
        discoverable=True,
        show_location=False,
        created_at=_NOW,
        updated_at=_NOW,
    )


def make_skill() -> CandidateSkill:
    return CandidateSkill(
        id=23,
        candidate_id=11,
        name="Python",
        name_key="python",
        level="advanced",
        created_at=_NOW,
        updated_at=_NOW,
    )


def make_service() -> AsyncMock:
    return AsyncMock()


def test_get_candidate_service_uses_injected_session() -> None:
    session = cast(AsyncSession, object())

    service = get_candidate_service(session)

    assert service._session is session


def test_create_profile_delegates_to_service_and_maps_response() -> None:
    async def scenario() -> None:
        service = make_service()
        service.create_profile.return_value = make_profile()
        body = CandidateProfileCreate(display_name="Ana")

        result = await create_profile(body, _USER, service)

        service.create_profile.assert_awaited_once_with(_USER.id, body)
        assert result.display_name == "Ana"
        assert result.preferences.work_modes == [WorkMode.REMOTE]
        assert result.visibility.discoverable is True
        assert result.created_at == _NOW

    asyncio.run(scenario())


def test_read_profile_delegates_to_service_and_maps_response() -> None:
    async def scenario() -> None:
        service = make_service()
        service.get_profile.return_value = make_profile()

        result = await read_profile(_USER, service)

        service.get_profile.assert_awaited_once_with(_USER.id)
        assert result.display_name == "Ana"
        assert result.city == "Berlin"
        assert result.languages == ["es", "en"]

    asyncio.run(scenario())


def test_update_profile_delegates_to_service_and_maps_response() -> None:
    async def scenario() -> None:
        service = make_service()
        service.update_profile.return_value = make_profile()
        body = CandidateProfileUpdate(summary="Updated summary")

        result = await update_profile(body, _USER, service)

        service.update_profile.assert_awaited_once_with(_USER.id, body)
        assert result.summary == "Backend developer"

    asyncio.run(scenario())


def test_delete_profile_delegates_to_service() -> None:
    async def scenario() -> None:
        service = make_service()

        await delete_profile(_USER, service)

        service.delete_profile.assert_awaited_once_with(_USER.id)

    asyncio.run(scenario())


def test_replace_preferences_delegates_and_maps_response() -> None:
    async def scenario() -> None:
        service = make_service()
        service.replace_preferences.return_value = make_profile()
        body = PreferencesUpdate(
            work_modes=[WorkMode.REMOTE],
            contract_types=[ContractType.FULL_TIME],
            preferred_locations=["Berlin"],
            interests=["Data"],
        )

        result = await replace_preferences(body, _USER, service)

        service.replace_preferences.assert_awaited_once_with(_USER.id, body)
        assert result.work_modes == [WorkMode.REMOTE]
        assert result.contract_types == [ContractType.FULL_TIME]
        assert result.preferred_locations == ["Berlin"]
        assert result.interests == ["Data"]

    asyncio.run(scenario())


def test_replace_visibility_delegates_and_maps_response() -> None:
    async def scenario() -> None:
        service = make_service()
        service.replace_visibility.return_value = make_profile()
        body = VisibilityUpdate(discoverable=True, show_location=False)

        result = await replace_visibility(body, _USER, service)

        service.replace_visibility.assert_awaited_once_with(_USER.id, body)
        assert result.discoverable is True
        assert result.show_location is False

    asyncio.run(scenario())


def test_list_skills_delegates_and_maps_each_skill() -> None:
    async def scenario() -> None:
        service = make_service()
        service.list_skills.return_value = [make_skill()]

        result = await list_skills(_USER, service)

        service.list_skills.assert_awaited_once_with(_USER.id)
        assert len(result) == 1
        assert result[0].id == 23
        assert result[0].name == "Python"
        assert result[0].level == SkillLevel.ADVANCED

    asyncio.run(scenario())


def test_add_skill_delegates_and_maps_response() -> None:
    async def scenario() -> None:
        service = make_service()
        service.add_skill.return_value = make_skill()
        body = SkillCreate(name="Python", level=SkillLevel.ADVANCED)

        result = await add_skill(body, _USER, service)

        service.add_skill.assert_awaited_once_with(_USER.id, body)
        assert result.id == 23
        assert result.name == "Python"
        assert result.level == SkillLevel.ADVANCED

    asyncio.run(scenario())


def test_update_skill_allows_owner_and_maps_response() -> None:
    async def scenario() -> None:
        service = make_service()
        service.get_skill_owner_id.return_value = _USER.id
        service.update_skill.return_value = make_skill()
        body = SkillUpdate(level=SkillLevel.ADVANCED)

        result = await update_skill(23, body, _USER, service)

        service.get_skill_owner_id.assert_awaited_once_with(23)
        service.update_skill.assert_awaited_once_with(23, _USER.id, body)
        assert result.name == "Python"
        assert result.level == SkillLevel.ADVANCED

    asyncio.run(scenario())


def test_update_skill_hides_resource_owned_by_another_user() -> None:
    async def scenario() -> None:
        service = make_service()
        service.get_skill_owner_id.return_value = _USER.id + 1
        body = SkillUpdate(name="Python")

        with pytest.raises(NotFoundError):
            await update_skill(23, body, _USER, service)

        service.get_skill_owner_id.assert_awaited_once_with(23)
        service.update_skill.assert_not_awaited()

    asyncio.run(scenario())


def test_delete_skill_allows_owner() -> None:
    async def scenario() -> None:
        service = make_service()
        service.get_skill_owner_id.return_value = _USER.id

        await delete_skill(23, _USER, service)

        service.get_skill_owner_id.assert_awaited_once_with(23)
        service.delete_skill.assert_awaited_once_with(23, _USER.id)

    asyncio.run(scenario())


def test_delete_skill_hides_resource_owned_by_another_user() -> None:
    async def scenario() -> None:
        service = make_service()
        service.get_skill_owner_id.return_value = _USER.id + 1

        with pytest.raises(NotFoundError):
            await delete_skill(23, _USER, service)

        service.get_skill_owner_id.assert_awaited_once_with(23)
        service.delete_skill.assert_not_awaited()

    asyncio.run(scenario())
