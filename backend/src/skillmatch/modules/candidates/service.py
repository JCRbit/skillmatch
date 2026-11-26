"""Use cases of the candidates module: profile, preferences, visibility and declared skills.

Every method receives the ``user_id`` of the *authenticated* caller, taken by the API layer from
the verified token and the database (never from the request body or path), and works only on
that user's rows. Authorisation by role and ownership checks are applied at the HTTP boundary
with the dependencies of :mod:`skillmatch.api.deps`; the scoping here is a second barrier.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Final

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.core.errors import NotFoundError
from skillmatch.modules.candidates.errors import (
    CandidateProfileAlreadyExistsError,
    CandidateProfileNotFoundError,
    SkillAlreadyDeclaredError,
    SkillLimitReachedError,
)
from skillmatch.modules.candidates.models import (
    CandidateConsent,
    CandidateProfile,
    CandidateSkill,
    ConsentPurpose,
)
from skillmatch.modules.candidates.projection import project_profile
from skillmatch.modules.candidates.repository import CandidateRepository
from skillmatch.modules.candidates.schemas import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    ConsentUpdate,
    PreferencesUpdate,
    SkillCreate,
    SkillUpdate,
    VisibilityUpdate,
)

MAX_SKILLS_PER_CANDIDATE: Final = 50
"""Upper bound of declared skills per candidate; keeps a profile (and its payloads) bounded."""

DEFAULT_POLICY_VERSION: Final = "2026-11"
"""Version of the privacy text recorded when a client does not send its own."""

_PROFILE_NOT_FOUND: Final = "Recurso no encontrado."
"""Same wording as a missing resource: a profile that is not shared is indistinguishable
from one that does not exist."""

_SKILL_NOT_FOUND: Final = "Recurso no encontrado."
"""Same wording as ``verify_resource_ownership`` so a missing skill and someone else's skill
are indistinguishable to the caller."""

_SKILL_NAME_UNIQUE_CONSTRAINT: Final = "uq_candidate_skills_candidate_id_name_key"


def _is_skill_name_unique_violation(exc: IntegrityError) -> bool:
    """Return whether the integrity error violates the skill-name unique constraint."""
    original = exc.orig

    # asyncpg exposes constraint_name directly on its database exceptions.
    constraint_name = getattr(original, "constraint_name", None)
    if isinstance(constraint_name, str):
        return constraint_name == _SKILL_NAME_UNIQUE_CONSTRAINT

    # Other PostgreSQL drivers, such as psycopg, expose it through diag.
    diagnostic = getattr(original, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)
    if isinstance(constraint_name, str):
        return constraint_name == _SKILL_NAME_UNIQUE_CONSTRAINT

    # SQLite does not expose constraint names, so identify the exact columns.
    sqlite_errorname = getattr(original, "sqlite_errorname", None)
    if not isinstance(sqlite_errorname, str):
        return False

    return (
        sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
        and str(original)
        == "UNIQUE constraint failed: candidate_skills.candidate_id, candidate_skills.name_key"
    )


_PROFILE_USER_UNIQUE_CONSTRAINT: Final = "ix_candidate_profiles_user_id"


def _is_profile_user_unique_violation(exc: IntegrityError) -> bool:
    """Return whether the integrity error violates the profile user uniqueness constraint."""
    original = exc.orig

    # asyncpg exposes constraint_name directly.
    constraint_name = getattr(original, "constraint_name", None)
    if isinstance(constraint_name, str):
        return constraint_name == _PROFILE_USER_UNIQUE_CONSTRAINT

    # Other PostgreSQL drivers expose it through diag.
    diagnostic = getattr(original, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)
    if isinstance(constraint_name, str):
        return constraint_name == _PROFILE_USER_UNIQUE_CONSTRAINT

    # SQLite does not expose constraint names.
    sqlite_errorname = getattr(original, "sqlite_errorname", None)
    if not isinstance(sqlite_errorname, str):
        return False

    return (
        sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
        and str(original) == "UNIQUE constraint failed: candidate_profiles.user_id"
    )


class CandidateService:
    """Creates, reads, updates and deletes the candidate's own data."""

    def __init__(self, session: AsyncSession) -> None:
        """Wire the service to the database session of the current request."""
        self._session = session
        self._repository = CandidateRepository(session)

    # ------------------------------------------------------------------ profile
    async def create_profile(self, user_id: int, data: CandidateProfileCreate) -> CandidateProfile:
        """Create the caller's profile, private and without preferences.

        Raises:
            CandidateProfileAlreadyExistsError: The caller already has a profile.
        """
        if await self._repository.get_profile_by_user(user_id) is not None:
            raise CandidateProfileAlreadyExistsError
        profile = CandidateProfile(
            user_id=user_id,
            display_name=data.display_name,
            summary=data.summary,
            city=data.city,
            languages=list(data.languages),
            work_modes=[],
            contract_types=[],
            preferred_locations=[],
            interests=[],
            discoverable=False,
            show_location=False,
        )
        self._repository.add(profile)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if _is_profile_user_unique_violation(exc):
                raise CandidateProfileAlreadyExistsError from exc
            raise
        await self._session.refresh(profile)
        return profile

    async def get_profile(self, user_id: int) -> CandidateProfile:
        """Return the caller's profile.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self._repository.get_profile_by_user(user_id)
        if profile is None:
            raise CandidateProfileNotFoundError
        return profile

    async def update_profile(self, user_id: int, data: CandidateProfileUpdate) -> CandidateProfile:
        """Apply a partial update to the caller's profile.

        Only the fields present in the request are changed.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self.get_profile(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        await self._session.commit()
        await self._session.refresh(profile)
        return profile

    async def delete_profile(self, user_id: int) -> None:
        """Delete the caller's profile and its skills. The account itself is kept.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self.get_profile(user_id)
        await self._repository.delete_profile(profile)
        await self._session.commit()

    # ------------------------------------------------- preferences and visibility
    async def replace_preferences(self, user_id: int, data: PreferencesUpdate) -> CandidateProfile:
        """Replace every preference of the caller's profile.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self.get_profile(user_id)
        profile.work_modes = [mode.value for mode in data.work_modes]
        profile.contract_types = [contract.value for contract in data.contract_types]
        profile.preferred_locations = list(data.preferred_locations)
        profile.interests = list(data.interests)
        await self._session.commit()
        await self._session.refresh(profile)
        return profile

    async def replace_visibility(self, user_id: int, data: VisibilityUpdate) -> CandidateProfile:
        """Set the visibility flags of the caller's profile.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self.get_profile(user_id)
        profile.discoverable = data.discoverable
        profile.show_location = data.show_location
        await self._session.commit()
        await self._session.refresh(profile)
        return profile

    # ------------------------------------------------------------------- skills
    async def list_skills(self, user_id: int) -> Sequence[CandidateSkill]:
        """Return the caller's declared skills ordered by name.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self.get_profile(user_id)
        return await self._repository.list_skills(profile.id)

    async def add_skill(self, user_id: int, data: SkillCreate) -> CandidateSkill:
        """Declare a new skill on the caller's profile.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
            SkillLimitReachedError: The profile already has the maximum number of skills.
            SkillAlreadyDeclaredError: The skill is already declared (ignoring capitalisation).
        """
        profile = await self._repository.get_profile_by_user_for_update(user_id)
        if profile is None:
            raise CandidateProfileNotFoundError
        if await self._repository.count_skills(profile.id) >= MAX_SKILLS_PER_CANDIDATE:
            raise SkillLimitReachedError
        name_key = data.name.casefold()
        if await self._repository.skill_name_exists(profile.id, name_key):
            raise SkillAlreadyDeclaredError
        skill = CandidateSkill(
            candidate_id=profile.id, name=data.name, name_key=name_key, level=data.level.value
        )
        self._repository.add(skill)
        await self._commit_skill_change()
        await self._session.refresh(skill)
        return skill

    async def get_skill_owner_id(self, skill_id: int) -> int:
        """Return the ``user_id`` that owns a skill, for the ownership check of the API layer.

        Raises:
            NotFoundError: No such skill. It is the same error a non-owner receives.
        """
        owner_id = await self._repository.get_skill_owner_id(skill_id)
        if owner_id is None:
            raise NotFoundError(_SKILL_NOT_FOUND)
        return owner_id

    async def update_skill(self, skill_id: int, user_id: int, data: SkillUpdate) -> CandidateSkill:
        """Change the name and/or level of one of the caller's skills.

        Raises:
            NotFoundError: The skill does not exist or is not the caller's.
            SkillAlreadyDeclaredError: The new name collides with another declared skill.
        """
        skill = await self._require_owned_skill(skill_id, user_id)
        if data.name is not None:
            name_key = data.name.casefold()
            if await self._repository.skill_name_exists(
                skill.candidate_id, name_key, excluding_skill_id=skill.id
            ):
                raise SkillAlreadyDeclaredError
            skill.name = data.name
            skill.name_key = name_key
        if data.level is not None:
            skill.level = data.level.value
        await self._commit_skill_change()
        await self._session.refresh(skill)
        return skill

    async def delete_skill(self, skill_id: int, user_id: int) -> None:
        """Remove one of the caller's skills.

        Raises:
            NotFoundError: The skill does not exist or is not the caller's.
        """
        skill = await self._require_owned_skill(skill_id, user_id)
        await self._repository.delete_skill(skill)
        await self._session.commit()

    # ----------------------------------------------------------------- helpers
    async def _require_owned_skill(self, skill_id: int, user_id: int) -> CandidateSkill:
        """Return the skill if it belongs to this user, otherwise raise ``NotFoundError``."""
        skill = await self._repository.get_owned_skill(skill_id, user_id)
        if skill is None:
            raise NotFoundError(_SKILL_NOT_FOUND)
        return skill

    async def _commit_skill_change(self) -> None:
        """Commit a skill change, translating only duplicate-name violations."""
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if _is_skill_name_unique_violation(exc):
                raise SkillAlreadyDeclaredError from exc
            raise

    # ------------------------------------------------------------------ consent
    async def list_consents(self, user_id: int) -> Sequence[CandidateConsent]:
        """Return the consent state of every purpose of the caller's profile.

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self.get_profile(user_id)
        return await self._repository.list_consents(profile.id)

    async def set_consent(
        self, user_id: int, purpose: ConsentPurpose, data: ConsentUpdate
    ) -> CandidateConsent:
        """Grant or withdraw consent for one purpose of the caller's profile.

        The decision is idempotent: repeating it keeps one row and does not move the date of
        the last real change. Withdrawing ``discovery`` also turns the ``discoverable`` flag
        off in the same transaction, so the profile stops being reachable immediately and the
        two never disagree (US-08: withdrawal must be effective, FR-019).

        Raises:
            CandidateProfileNotFoundError: The caller has no profile yet.
        """
        profile = await self.get_profile(user_id)
        now = datetime.now(UTC)
        policy_version = data.policy_version or DEFAULT_POLICY_VERSION
        consent = await self._repository.get_consent(profile.id, purpose.value)
        if consent is None:
            consent = CandidateConsent(
                candidate_id=profile.id,
                purpose=purpose.value,
                granted=False,
                policy_version=policy_version,
            )
            self._repository.add_consent(consent)
        if consent.granted != data.granted:
            consent.granted = data.granted
            consent.policy_version = policy_version
            if data.granted:
                consent.granted_at = now
            else:
                consent.revoked_at = now
        if purpose is ConsentPurpose.DISCOVERY:
            profile.discoverable = data.granted
        await self._session.commit()
        await self._session.refresh(consent)
        return consent

    # -------------------------------------------------------------- projection
    async def get_projection(self, candidate_id: int) -> dict[str, Any]:
        """Return the pseudonymised projection of one profile for a company (B-06).

        The profile is reachable only when the candidate granted ``DISCOVERY`` *and* kept the
        ``discoverable`` flag on; otherwise it is answered with ``NotFoundError``, the same
        response as a profile that does not exist, so a company cannot enumerate candidates.

        Args:
            candidate_id: Id of the profile the company wants to see.

        Returns:
            The allowlisted projection of :func:`project_profile`.

        Raises:
            NotFoundError: The profile does not exist or is not shared.
        """
        profile = await self._repository.get_profile_by_id(candidate_id)
        if profile is None or not profile.discoverable:
            raise NotFoundError(_PROFILE_NOT_FOUND)
        granted = {
            consent.purpose
            for consent in await self._repository.list_consents(profile.id)
            if consent.granted
        }
        if ConsentPurpose.DISCOVERY.value not in granted:
            raise NotFoundError(_PROFILE_NOT_FOUND)
        skills = await self._repository.list_skills(profile.id)
        return project_profile(
            profile,
            skills,
            location_consented=ConsentPurpose.LOCATION.value in granted,
            skills_consented=ConsentPurpose.SKILLS.value in granted,
        )
