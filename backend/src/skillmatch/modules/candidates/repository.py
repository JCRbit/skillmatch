"""Persistence access of the candidates module.

The repository only reads and stages changes; committing, rolling back and every business rule
belong to :class:`skillmatch.modules.candidates.service.CandidateService`. Every query that
returns candidate data is scoped by the owner's ``user_id`` (or by a profile that was itself
loaded through it), so another candidate's rows are unreachable by construction.
"""

from collections.abc import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.modules.candidates.models import CandidateProfile, CandidateProject, CandidateSkill


class CandidateRepository:
    """Queries and staged changes for candidate profiles and their skills."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to the session of the current request."""
        self._session = session

    async def get_profile_by_user(self, user_id: int) -> CandidateProfile | None:
        """Return the profile owned by this user, if any."""
        result = await self._session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_by_user_for_update(self, user_id: int) -> CandidateProfile | None:
        """Return the user's profile while locking its row for the current transaction."""
        result = await self._session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id).with_for_update()
        )
        return result.scalar_one_or_none()

    def add(self, entity: CandidateProfile | CandidateSkill | CandidateProject) -> None:
        """Stage a new profile, skill, or project for insertion."""
        self._session.add(entity)

    async def delete_profile(self, profile: CandidateProfile) -> None:
        """Stage the deletion of a profile and of all its skills.

        Skills are removed explicitly instead of relying on ``ON DELETE CASCADE`` so the result
        is the same on every database, including SQLite without foreign-key enforcement.
        """
        await self._session.execute(
            delete(CandidateSkill).where(CandidateSkill.candidate_id == profile.id)
        )
        await self._session.delete(profile)

    async def list_skills(self, profile_id: int) -> Sequence[CandidateSkill]:
        """Return the skills of a profile ordered by name."""
        result = await self._session.execute(
            select(CandidateSkill)
            .where(CandidateSkill.candidate_id == profile_id)
            .order_by(CandidateSkill.name_key)
        )
        return result.scalars().all()

    async def count_skills(self, profile_id: int) -> int:
        """Return how many skills a profile has declared."""
        result = await self._session.execute(
            select(func.count())
            .select_from(CandidateSkill)
            .where(CandidateSkill.candidate_id == profile_id)
        )
        return result.scalar_one()

    async def skill_name_exists(
        self, profile_id: int, name_key: str, *, excluding_skill_id: int | None = None
    ) -> bool:
        """Whether the profile already has a skill with this case-folded name."""
        statement = (
            select(func.count())
            .select_from(CandidateSkill)
            .where(
                CandidateSkill.candidate_id == profile_id,
                CandidateSkill.name_key == name_key,
            )
        )
        if excluding_skill_id is not None:
            statement = statement.where(CandidateSkill.id != excluding_skill_id)
        result = await self._session.execute(statement)
        return result.scalar_one() > 0

    async def get_skill_owner_id(self, skill_id: int) -> int | None:
        """Return the ``user_id`` that owns a skill, whoever is asking.

        Callers must pass the result to ``verify_resource_ownership`` before acting on the skill.
        """
        result = await self._session.execute(
            select(CandidateProfile.user_id)
            .join(CandidateSkill, CandidateSkill.candidate_id == CandidateProfile.id)
            .where(CandidateSkill.id == skill_id)
        )
        return result.scalar_one_or_none()

    async def get_owned_skill(self, skill_id: int, user_id: int) -> CandidateSkill | None:
        """Return a skill only if it belongs to this user's profile."""
        result = await self._session.execute(
            select(CandidateSkill)
            .join(CandidateProfile, CandidateSkill.candidate_id == CandidateProfile.id)
            .where(CandidateSkill.id == skill_id, CandidateProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete_skill(self, skill: CandidateSkill) -> None:
        """Stage the deletion of one skill."""
        await self._session.delete(skill)

    # --------------------------------------------------------------------- projects (S-06)
    async def list_projects(self, profile_id: int) -> Sequence[CandidateProject]:
        """Return projects of a profile ordered by newest project date, then id."""
        result = await self._session.execute(
            select(CandidateProject)
            .where(CandidateProject.candidate_id == profile_id)
            .order_by(CandidateProject.project_date.desc(), CandidateProject.id.desc())
        )
        return result.scalars().all()

    async def get_project_owner_id(self, project_id: int) -> int | None:
        """Return the user_id that owns a project."""
        result = await self._session.execute(
            select(CandidateProfile.user_id)
            .join(CandidateProject, CandidateProject.candidate_id == CandidateProfile.id)
            .where(CandidateProject.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_owned_project(self, project_id: int, user_id: int) -> CandidateProject | None:
        """Return a project only if it belongs to this user's profile."""
        result = await self._session.execute(
            select(CandidateProject)
            .join(CandidateProfile, CandidateProject.candidate_id == CandidateProfile.id)
            .where(CandidateProject.id == project_id, CandidateProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete_project(self, project: CandidateProject) -> None:
        """Stage deletion of a project."""
        await self._session.delete(project)
