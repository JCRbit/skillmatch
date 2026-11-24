"""Candidate-specific errors, rendered as RFC 9457 problem details by the API layer."""

from typing import ClassVar

from skillmatch.core.errors import ConflictError, NotFoundError


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
