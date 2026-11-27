"""Candidate-specific errors, rendered as RFC 9457 problem details by the API layer."""

from http import HTTPStatus
from typing import ClassVar

from skillmatch.core.errors import AppError, ConflictError, NotFoundError


class CandidateProfileNotFoundError(NotFoundError):
    """The authenticated candidate has not created a profile yet."""

    code: ClassVar[str] = "candidate_profile_not_found"
    title: ClassVar[str] = "Candidate profile not found"


class CandidateProfileAlreadyExistsError(ConflictError):
    """The authenticated candidate already has a profile."""

    code: ClassVar[str] = "candidate_profile_already_exists"
    title: ClassVar[str] = "Candidate profile already exists"


class SkillAlreadyDeclaredError(ConflictError):
    """The candidate already declared a skill with this name."""

    code: ClassVar[str] = "skill_already_declared"
    title: ClassVar[str] = "Skill already declared"


class SkillLimitReachedError(ConflictError):
    """The candidate reached the maximum number of declared skills."""

    code: ClassVar[str] = "skill_limit_reached"
    title: ClassVar[str] = "Skill limit reached"


class EvidenceCanonicalSkillNotFoundError(AppError):
    """The canonical skill identifier is not in the official taxonomy."""

    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    code: ClassVar[str] = "evidence_canonical_skill_not_found"
    title: ClassVar[str] = "Canonical skill not found"


class EvidenceCanonicalIdConflictError(ConflictError):
    """The project already has evidence for this canonical skill."""

    code: ClassVar[str] = "evidence_canonical_id_conflict"
    title: ClassVar[str] = "Evidence canonical ID conflict"
