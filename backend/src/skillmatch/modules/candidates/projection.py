"""Pseudonymised projection of a candidate profile (US-15, FR-012, D-09).

The projection is built by **allowlist**, never by removing fields from a full representation: a
field that is not named here cannot appear in the output, so adding a column to the model can
never leak it by accident. The allowed set depends on the stage the viewer is in and on the
consent the candidate gave (US-08):

``DISCOVERY``
    What a company may see while browsing. Pseudonym only, no identity, no contact and no
    repository links (D-09: hide links and usernames in the initial view).
``MATCH``
    After a verified mutual interest. It is declared here so the allowlist is the single source
    of truth, but the endpoints that reach this stage belong to task B-07.

Blocked fields are documented in :data:`BLOCKED_FIELDS` so the non-leakage tests can assert
their absence without repeating the list.
"""

from collections.abc import Sequence
from enum import StrEnum
from typing import Any, Final

from skillmatch.modules.candidates.models import CandidateProfile, CandidateSkill


class ProjectionStage(StrEnum):
    """How much of the profile a viewer is allowed to see."""

    DISCOVERY = "discovery"
    MATCH = "match"


_DISCOVERY_FIELDS: Final[frozenset[str]] = frozenset(
    {"display_name", "summary", "city", "languages", "skills"}
)
"""Fields a company may see in the ``DISCOVERY`` stage.

``city`` is only included when the candidate both hid nothing and consented to ``LOCATION``;
``skills`` only when they consented to ``SKILLS``. ``summary`` and ``languages`` are part of the
pseudonymised profile because they describe competences, not identity.
"""

_MATCH_FIELDS: Final[frozenset[str]] = _DISCOVERY_FIELDS | {"contact"}
"""Fields allowed after a verified mutual interest. ``contact`` is filled by task B-07."""

ALLOWED_FIELDS: Final[dict[ProjectionStage, frozenset[str]]] = {
    ProjectionStage.DISCOVERY: _DISCOVERY_FIELDS,
    ProjectionStage.MATCH: _MATCH_FIELDS,
}
"""The allowlist itself: stage -> fields that projection may ever contain."""

BLOCKED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "id",
        "user_id",
        "email",
        "role",
        "status",
        "password_hash",
        "created_at",
        "updated_at",
        "granted_at",
        "revoked_at",
        "policy_version",
        "discoverable",
        "show_location",
        "preferred_locations",
        "interests",
        "work_modes",
        "contract_types",
        "name_key",
        "skill_id",
        "candidate_id",
        "github_url",
        "repository_url",
        "username",
    }
)
"""Fields that must never appear in a projection, at any stage.

It covers identity (``user_id``, ``email``, ``role``), internal bookkeeping (ids, timestamps),
the candidate's private preferences, the consent bookkeeping and, per D-09, the links and
usernames that would re-identify the person. The tests assert on this list.
"""


def _skill_view(skill: CandidateSkill) -> dict[str, Any]:
    """Project one skill: its name and declared level, never its row id."""
    return {"name": skill.name, "level": skill.level}


def project_profile(
    profile: CandidateProfile,
    skills: Sequence[CandidateSkill],
    *,
    stage: ProjectionStage = ProjectionStage.DISCOVERY,
    location_consented: bool = False,
    skills_consented: bool = False,
) -> dict[str, Any]:
    """Build the pseudonymised view of a profile for one stage.

    Args:
        profile: The stored profile.
        skills: The candidate's declared skills.
        stage: How much the viewer is allowed to see.
        location_consented: Whether the candidate granted the ``LOCATION`` purpose.
        skills_consented: Whether the candidate granted the ``SKILLS`` purpose.

    Returns:
        A dictionary that contains only allowed fields. ``city`` appears only when the candidate
        kept ``show_location`` on *and* consented to ``LOCATION``; ``skills`` only with the
        ``SKILLS`` purpose. Absent means "not shared", never ``null``, so a client cannot tell a
        hidden value from an empty one.
    """
    allowed = ALLOWED_FIELDS[stage]
    projected: dict[str, Any] = {}

    if "display_name" in allowed:
        projected["display_name"] = profile.display_name
    if "summary" in allowed and profile.summary is not None:
        projected["summary"] = profile.summary
    if "languages" in allowed and profile.languages:
        projected["languages"] = list(profile.languages)
    if "city" in allowed and profile.show_location and location_consented and profile.city:
        projected["city"] = profile.city
    if "skills" in allowed and skills_consented:
        projected["skills"] = [_skill_view(skill) for skill in skills]

    return projected
