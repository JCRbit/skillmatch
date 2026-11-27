"""Use cases of the candidates module: profile, preferences, visibility and declared skills.

Every method receives the ``user_id`` of the *authenticated* caller, taken by the API layer from
the verified token and the database (never from the request body or path), and works only on
that user's rows. Authorisation by role and ownership checks are applied at the HTTP boundary
with the dependencies of :mod:`skillmatch.api.deps`; the scoping here is a second barrier.
"""

import re
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Final

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.core.errors import NotFoundError
from skillmatch.modules.candidates.errors import (
    CandidateProfileAlreadyExistsError,
    CandidateProfileNotFoundError,
    EvidenceCanonicalIdConflictError,
    EvidenceCanonicalSkillNotFoundError,
    SkillAlreadyDeclaredError,
    SkillLimitReachedError,
)
from skillmatch.modules.candidates.models import (
    CandidateConsent,
    CandidateProfile,
    CandidateProject,
    CandidateProjectEvidence,
    CandidateProjectEvidenceAudit,
    CandidateSkill,
    ConsentPurpose,
    EvidenceStatus,
)
from skillmatch.modules.candidates.repository import CandidateRepository
from skillmatch.modules.candidates.schemas import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProjectCreate,
    CandidateProjectUpdate,
    ConsentUpdate,
    EvidenceReviewRequest,
    PreferencesUpdate,
    SkillCreate,
    SkillUpdate,
    VisibilityUpdate,
)
from skillmatch.modules.skills import build_alias_index, load_taxonomy, normalize_alias

MAX_SKILLS_PER_CANDIDATE: Final = 50
DEFAULT_POLICY_VERSION: Final = "2026-11"
"""Upper bound of declared skills per candidate; keeps a profile (and its payloads) bounded."""

_SKILL_NOT_FOUND: Final = "Recurso no encontrado."
"""Same wording as ``verify_resource_ownership`` so a missing skill and someone else's skill
are indistinguishable to the caller."""

_PROJECT_NOT_FOUND: Final = "Recurso no encontrado."

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


_EVIDENCE_CANONICAL_UNIQUE_CONSTRAINT: Final = "uq_candidate_project_evidences_project_canonical"


def _is_evidence_canonical_unique_violation(exc: IntegrityError) -> bool:
    """Return whether the integrity error violates project evidence canonical uniqueness."""
    original = exc.orig

    constraint_name = getattr(original, "constraint_name", None)
    if isinstance(constraint_name, str):
        return constraint_name == _EVIDENCE_CANONICAL_UNIQUE_CONSTRAINT

    diagnostic = getattr(original, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)
    if isinstance(constraint_name, str):
        return constraint_name == _EVIDENCE_CANONICAL_UNIQUE_CONSTRAINT

    sqlite_errorname = getattr(original, "sqlite_errorname", None)
    if not isinstance(sqlite_errorname, str):
        return False

    return (
        sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
        and str(original)
        == "UNIQUE constraint failed: candidate_project_evidences.project_id, "
        "candidate_project_evidences.canonical_id"
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

    # ------------------------------------------------------------------ projects (S-06)
    async def list_projects(self, user_id: int) -> Sequence[CandidateProject]:
        """Return the caller's projects."""
        profile = await self.get_profile(user_id)
        return await self._repository.list_projects(profile.id)

    async def create_project(
        self, user_id: int, data: CandidateProjectCreate
    ) -> tuple[CandidateProject, list[CandidateProjectEvidence]]:
        """Create a manual project and persist evidence proposals."""
        profile = await self.get_profile(user_id)
        project = CandidateProject(
            candidate_id=profile.id,
            name=data.name,
            description=data.description,
            role=data.role,
            stack=list(data.stack),
            source_type=data.source_type.value,
            source_url=data.source_url,
            project_date=data.project_date,
        )
        self._repository.add(project)
        await self._session.flush()
        await self._sync_evidences(project)
        await self._session.commit()
        await self._session.refresh(project)
        evidences = await self._repository.list_evidences(project.id)
        return project, list(evidences)

    async def get_project_owner_id(self, project_id: int) -> int:
        """Return owner user_id for ownership checks."""
        owner_id = await self._repository.get_project_owner_id(project_id)
        if owner_id is None:
            raise NotFoundError(_PROJECT_NOT_FOUND)
        return owner_id

    async def get_project(
        self, project_id: int, user_id: int
    ) -> tuple[CandidateProject, list[CandidateProjectEvidence]]:
        """Return an owned project and its evidences."""
        project = await self._require_owned_project(project_id, user_id)
        evidences = await self._repository.list_evidences(project.id)
        return project, list(evidences)

    async def update_project(
        self, project_id: int, user_id: int, data: CandidateProjectUpdate
    ) -> tuple[CandidateProject, list[CandidateProjectEvidence]]:
        """Update an owned project and sync new evidence proposals."""
        project = await self._require_owned_project(project_id, user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "source_type" and value is not None:
                setattr(project, field, value.value)
            else:
                setattr(project, field, value)
        await self._session.flush()
        await self._sync_evidences(project)
        await self._session.commit()
        await self._session.refresh(project)
        evidences = await self._repository.list_evidences(project.id)
        return project, list(evidences)

    async def delete_project(self, project_id: int, user_id: int) -> None:
        """Delete an owned project."""
        project = await self._require_owned_project(project_id, user_id)
        await self._repository.delete_project(project)
        await self._session.commit()

    async def _require_owned_project(self, project_id: int, user_id: int) -> CandidateProject:
        project = await self._repository.get_owned_project(project_id, user_id)
        if project is None:
            raise NotFoundError(_PROJECT_NOT_FOUND)
        return project

    # ------------------------------------------------------------------ evidences (S-07)
    async def list_evidences(self, project_id: int, user_id: int) -> list[CandidateProjectEvidence]:
        """Return evidences for an owned project."""
        await self._require_owned_project(project_id, user_id)
        return list(await self._repository.list_evidences(project_id))

    async def get_evidence_owner_id(self, evidence_id: int) -> int:
        """Return owner user_id for an evidence."""
        owner_id = await self._repository.get_evidence_owner_id(evidence_id)
        if owner_id is None:
            raise NotFoundError(_PROJECT_NOT_FOUND)
        return owner_id

    async def review_evidence(
        self,
        project_id: int,
        evidence_id: int,
        user_id: int,
        data: EvidenceReviewRequest,
    ) -> CandidateProjectEvidence:
        """Apply a review action to an evidence and record an audit trail."""
        await self._require_owned_project(project_id, user_id)
        evidence = await self._repository.get_owned_evidence(evidence_id, user_id)
        if evidence is None or evidence.project_id != project_id:
            raise NotFoundError(_PROJECT_NOT_FOUND)

        before = self._evidence_snapshot(evidence)
        from_status = EvidenceStatus(evidence.status)

        if data.action == "confirm":
            evidence.status = EvidenceStatus.CONFIRMED.value
        elif data.action == "withdraw":
            evidence.status = EvidenceStatus.WITHDRAWN.value
        elif data.action == "correct":
            if data.canonical_id is not None:
                taxonomy = load_taxonomy()
                skill = next((s for s in taxonomy if s.canonical_id == data.canonical_id), None)
                if skill is None:
                    raise EvidenceCanonicalSkillNotFoundError(
                        f"Unknown canonical skill: {data.canonical_id!r}"
                    )
                evidence.canonical_id = skill.canonical_id
                evidence.skill_label = skill.skill
            elif data.skill_label is not None:
                evidence.skill_label = data.skill_label
            if data.matched_term is not None:
                evidence.matched_term = data.matched_term
            evidence.status = EvidenceStatus.CORRECTED.value
        if data.note is not None:
            evidence.note = data.note

        to_status = EvidenceStatus(evidence.status)
        after = self._evidence_snapshot(evidence)
        self._repository.add_audit(
            CandidateProjectEvidenceAudit(
                evidence_id=evidence.id,
                project_id=project_id,
                actor_user_id=user_id,
                action=data.action,
                from_status=from_status.value,
                to_status=to_status.value,
                before=before,
                after=after,
            )
        )
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if _is_evidence_canonical_unique_violation(exc):
                raise EvidenceCanonicalIdConflictError(
                    "Evidence already exists for this canonical skill in the project"
                ) from exc
            raise
        await self._session.refresh(evidence)
        return evidence

    async def list_evidence_audits(
        self, project_id: int, evidence_id: int, user_id: int
    ) -> list[CandidateProjectEvidenceAudit]:
        """Return audit trail for an owned evidence."""
        await self._require_owned_project(project_id, user_id)
        evidence = await self._repository.get_owned_evidence(evidence_id, user_id)
        if evidence is None or evidence.project_id != project_id:
            raise NotFoundError(_PROJECT_NOT_FOUND)
        return list(await self._repository.list_evidence_audits(evidence_id))

    @staticmethod
    def _evidence_snapshot(evidence: CandidateProjectEvidence) -> dict[str, str | None]:
        return {
            "canonical_id": evidence.canonical_id,
            "skill_label": evidence.skill_label,
            "matched_term": evidence.matched_term,
            "source": evidence.source,
            "status": evidence.status,
            "note": evidence.note,
        }

    async def _sync_evidences(self, project: CandidateProject) -> None:
        """Persist newly detected proposals without overwriting reviewed signals."""
        proposals = self.propose_evidence(project)
        existing = {e.canonical_id: e for e in await self._repository.list_evidences(project.id)}
        for proposal in proposals:
            canonical_id = proposal["canonical_id"]
            if canonical_id in existing:
                evidence = existing[canonical_id]
                if evidence.status == EvidenceStatus.PROPOSED.value:
                    evidence.skill_label = proposal["skill"]
                    evidence.matched_term = proposal["matched_term"]
                    evidence.source = proposal["source"]
                continue
            self._repository.add(
                CandidateProjectEvidence(
                    project_id=project.id,
                    candidate_id=project.candidate_id,
                    canonical_id=canonical_id,
                    skill_label=proposal["skill"],
                    matched_term=proposal["matched_term"],
                    source=proposal["source"],
                    status=EvidenceStatus.PROPOSED.value,
                )
            )

    def propose_evidence(self, project: CandidateProject) -> list[dict[str, str]]:
        """Propose canonical skills from project text using taxonomy aliases.

        Manual, deterministic text matching only. No code execution.
        """
        taxonomy = load_taxonomy()
        skills_by_id = {s.canonical_id: s for s in taxonomy}
        alias_index = build_alias_index(taxonomy)

        proposals: dict[str, dict[str, str]] = {}

        # 1) Stack items: exact normalized alias resolution
        for item in project.stack:
            canonical_id = alias_index.get(normalize_alias(item))
            if canonical_id and canonical_id not in proposals:
                skill = skills_by_id[canonical_id]
                proposals[canonical_id] = {
                    "canonical_id": canonical_id,
                    "skill": skill.skill,
                    "matched_term": item,
                    "source": "stack",
                }

        # 2) Free text fields: conservative word-boundary matching
        text_sources = [
            ("name", project.name),
            ("role", project.role),
            ("description", project.description),
        ]
        safe_aliases: list[tuple[str, str, str]] = []
        seen: set[tuple[str, str]] = set()
        for skill in taxonomy:
            for alias in (skill.skill, *skill.aliases):
                norm = normalize_alias(alias)
                if not norm or len(norm) < 3:
                    continue
                key = (norm, skill.canonical_id)
                if key in seen:
                    continue
                seen.add(key)
                safe_aliases.append((norm, skill.canonical_id, alias))
        safe_aliases.sort(key=lambda x: len(x[0]), reverse=True)

        for source_name, text in text_sources:
            norm_text = f" {normalize_alias(text)} "
            for norm_alias, canonical_id, original_alias in safe_aliases:
                if canonical_id in proposals:
                    continue
                pattern = r"(?<![a-z0-9])" + re.escape(norm_alias) + r"(?![a-z0-9])"
                if re.search(pattern, norm_text):
                    skill = skills_by_id[canonical_id]
                    proposals[canonical_id] = {
                        "canonical_id": canonical_id,
                        "skill": skill.skill,
                        "matched_term": original_alias,
                        "source": source_name,
                    }

        return list(proposals.values())

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
