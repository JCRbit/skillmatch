"""HTTP endpoints of the candidate: own profile, preferences, visibility and declared skills.

====================================  ======  ==================================================
Endpoint                              Access  Purpose
====================================  ======  ==================================================
``POST   /candidates/me``             talent  Create the caller's profile.
``GET    /candidates/me``             talent  Read it.
``PATCH  /candidates/me``             talent  Change some of its fields.
``DELETE /candidates/me``             talent  Delete it and its skills (the account stays).
``PUT    /candidates/me/preferences`` talent  Replace the preferences.
``PUT    /candidates/me/visibility``  talent  Set the visibility flags.
``GET    /candidates/me/skills``      talent  List the declared skills.
``POST   /candidates/me/skills``      talent  Declare a skill.
``PATCH  /candidates/me/skills/{id}`` talent  Change a skill.
``DELETE /candidates/me/skills/{id}`` talent  Remove a skill.
====================================  ======  ==================================================

There is no identifier of a candidate anywhere in these URLs or bodies: the profile is always the
one of the authenticated user (:data:`TalentDep`). The only client-supplied identifier is a skill
id, and it is checked with :func:`skillmatch.api.deps.verify_resource_ownership` before use.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, status

from skillmatch.api.deps import SessionDep, require_roles, verify_resource_ownership
from skillmatch.api.problems import problem_responses
from skillmatch.modules.candidates.models import (
    CandidateProject,
    CandidateProjectEvidence,
    ConsentPurpose,
)
from skillmatch.modules.candidates.schemas import (
    CandidateProfileCreate,
    CandidateProfileRead,
    CandidateProfileUpdate,
    CandidateProjectCreate,
    CandidateProjectRead,
    CandidateProjectUpdate,
    CandidateProjectWithProposalsRead,
    CandidateProjection,
    ConsentRead,
    ConsentsRead,
    ConsentUpdate,
    EvidenceAuditRead,
    EvidenceProposalRead,
    EvidenceRead,
    EvidenceReviewRequest,
    PreferencesRead,
    PreferencesUpdate,
    SkillCreate,
    SkillRead,
    SkillUpdate,
    VisibilityRead,
    VisibilityUpdate,
)
from skillmatch.modules.candidates.service import CandidateService
from skillmatch.modules.identity.models import User, UserRole

router = APIRouter(prefix="/candidates", tags=["candidates"])

TalentDep = Annotated[User, Depends(require_roles(UserRole.TALENTO))]
"""The authenticated candidate. Any other role is answered with ``403 permission_denied``."""

CompanyDep = Annotated[User, Depends(require_roles(UserRole.EMPRESA))]
"""The authenticated company. Any other role is answered with ``403 permission_denied``."""

_MAX_DB_INTEGER = 2_147_483_647
SkillIdPath = Annotated[int, Path(ge=1, le=_MAX_DB_INTEGER, description="Id of a declared skill.")]
"""Path parameter of a skill; bounded so it always fits the database integer type."""
ProjectIdPath = Annotated[int, Path(ge=1, le=_MAX_DB_INTEGER, description="Id of a project.")]
EvidenceIdPath = Annotated[int, Path(ge=1, le=_MAX_DB_INTEGER, description="Id of an evidence.")]

CandidateIdPath = Annotated[
    int, Path(ge=1, le=_MAX_DB_INTEGER, description="Id of a candidate profile.")
]
"""Path parameter of a candidate profile; bounded so it always fits the database integer type."""
ConsentPurposePath = Annotated[ConsentPurpose, Path(description="Purpose the decision applies to.")]


def get_candidate_service(session: SessionDep) -> CandidateService:
    """Build the :class:`CandidateService` for one request."""
    return CandidateService(session)


CandidateServiceDep = Annotated[CandidateService, Depends(get_candidate_service)]
"""The candidate service of the current request."""


# --------------------------------------------------------------------------- profile
@router.post(
    "/me",
    status_code=status.HTTP_201_CREATED,
    summary="Create my candidate profile",
    responses=problem_responses(401, 403, 409, 422),
)
async def create_profile(
    body: CandidateProfileCreate, current_user: TalentDep, service: CandidateServiceDep
) -> CandidateProfileRead:
    """Create the caller's profile.

    A new profile is private (not discoverable, location hidden) and has no preferences. A
    candidate has at most one profile.
    """
    profile = await service.create_profile(current_user.id, body)
    return CandidateProfileRead.from_profile(profile)


@router.get(
    "/me",
    summary="Read my candidate profile",
    responses=problem_responses(401, 403, 404),
)
async def read_profile(
    current_user: TalentDep, service: CandidateServiceDep
) -> CandidateProfileRead:
    """Return the caller's own profile, preferences and visibility flags."""
    profile = await service.get_profile(current_user.id)
    return CandidateProfileRead.from_profile(profile)


@router.patch(
    "/me",
    summary="Update my candidate profile",
    responses=problem_responses(401, 403, 404, 422),
)
async def update_profile(
    body: CandidateProfileUpdate, current_user: TalentDep, service: CandidateServiceDep
) -> CandidateProfileRead:
    """Change only the profile fields present in the body."""
    profile = await service.update_profile(current_user.id, body)
    return CandidateProfileRead.from_profile(profile)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete my candidate profile",
    responses=problem_responses(401, 403, 404),
)
async def delete_profile(current_user: TalentDep, service: CandidateServiceDep) -> None:
    """Delete the profile with its skills, preferences and visibility flags.

    The account is not deleted and the candidate can create a new profile afterwards.
    """
    await service.delete_profile(current_user.id)


# --------------------------------------------------------- preferences and visibility
@router.put(
    "/me/preferences",
    summary="Replace my preferences",
    responses=problem_responses(401, 403, 404, 422),
)
async def replace_preferences(
    body: PreferencesUpdate, current_user: TalentDep, service: CandidateServiceDep
) -> PreferencesRead:
    """Replace work modes, contract types, preferred locations and interests."""
    profile = await service.replace_preferences(current_user.id, body)
    return PreferencesRead.model_validate(profile)


@router.put(
    "/me/visibility",
    summary="Set my visibility flags",
    responses=problem_responses(401, 403, 404, 422),
)
async def replace_visibility(
    body: VisibilityUpdate, current_user: TalentDep, service: CandidateServiceDep
) -> VisibilityRead:
    """Set whether the profile is discoverable and whether the city may be shown."""
    profile = await service.replace_visibility(current_user.id, body)
    return VisibilityRead.model_validate(profile)


# ------------------------------------------------------------------------- skills
@router.get(
    "/me/skills",
    summary="List my declared skills",
    responses=problem_responses(401, 403, 404),
)
async def list_skills(current_user: TalentDep, service: CandidateServiceDep) -> list[SkillRead]:
    """Return the caller's declared skills ordered by name."""
    skills = await service.list_skills(current_user.id)
    return [SkillRead.from_skill(skill) for skill in skills]


@router.post(
    "/me/skills",
    status_code=status.HTTP_201_CREATED,
    summary="Declare a skill",
    responses=problem_responses(401, 403, 404, 409, 422),
)
async def add_skill(
    body: SkillCreate, current_user: TalentDep, service: CandidateServiceDep
) -> SkillRead:
    """Declare a skill. Names are unique per candidate, ignoring capitalisation."""
    skill = await service.add_skill(current_user.id, body)
    return SkillRead.from_skill(skill)


@router.patch(
    "/me/skills/{skill_id}",
    summary="Update a declared skill",
    responses=problem_responses(401, 403, 404, 409, 422),
)
async def update_skill(
    skill_id: SkillIdPath,
    body: SkillUpdate,
    current_user: TalentDep,
    service: CandidateServiceDep,
) -> SkillRead:
    """Change the name and/or level of one of the caller's skills.

    A skill that does not exist and a skill of another candidate both answer ``404``.
    """
    owner_id = await service.get_skill_owner_id(skill_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    skill = await service.update_skill(skill_id, current_user.id, body)
    return SkillRead.from_skill(skill)


@router.delete(
    "/me/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a declared skill",
    responses=problem_responses(401, 403, 404),
)
async def delete_skill(
    skill_id: SkillIdPath, current_user: TalentDep, service: CandidateServiceDep
) -> None:
    """Remove one of the caller's skills.

    A skill that does not exist and a skill of another candidate both answer ``404``.
    """
    owner_id = await service.get_skill_owner_id(skill_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    await service.delete_skill(skill_id, current_user.id)


# ------------------------------------------------------------------------- projects (S-06)
def _project_with_evidences(
    project: CandidateProject, evidences: list[CandidateProjectEvidence]
) -> CandidateProjectWithProposalsRead:
    """Build project response with persisted evidences and backward-compatible proposals."""
    proposals = [
        EvidenceProposalRead(
            canonical_id=e.canonical_id,
            skill=e.skill_label,
            matched_term=e.matched_term,
            source=e.source,
        )
        for e in evidences
        if e.status != "withdrawn"
    ]
    return CandidateProjectWithProposalsRead(
        **CandidateProjectRead.from_project(project).model_dump(),
        evidence_proposals=proposals,
        evidences=[EvidenceRead.from_evidence(e) for e in evidences],
    )


@router.get(
    "/me/projects",
    summary="List my manual projects",
    responses=problem_responses(401, 403, 404),
)
async def list_projects(
    current_user: TalentDep, service: CandidateServiceDep
) -> list[CandidateProjectRead]:
    """Return the caller's manually entered projects."""
    projects = await service.list_projects(current_user.id)
    return [CandidateProjectRead.from_project(p) for p in projects]


@router.post(
    "/me/projects",
    status_code=status.HTTP_201_CREATED,
    summary="Create a manual project",
    responses=problem_responses(401, 403, 404, 422),
)
async def create_project(
    body: CandidateProjectCreate, current_user: TalentDep, service: CandidateServiceDep
) -> CandidateProjectWithProposalsRead:
    """Create a manual project and return evidence proposals from text."""
    project, evidences = await service.create_project(current_user.id, body)
    return _project_with_evidences(project, list(evidences))


@router.get(
    "/me/projects/{project_id}",
    summary="Read one of my projects",
    responses=problem_responses(401, 403, 404),
)
async def read_project(
    project_id: ProjectIdPath, current_user: TalentDep, service: CandidateServiceDep
) -> CandidateProjectWithProposalsRead:
    """Return one owned project with evidence proposals."""
    owner_id = await service.get_project_owner_id(project_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    project, evidences = await service.get_project(project_id, current_user.id)
    return _project_with_evidences(project, list(evidences))


@router.patch(
    "/me/projects/{project_id}",
    summary="Update one of my projects",
    responses=problem_responses(401, 403, 404, 422),
)
async def update_project(
    project_id: ProjectIdPath,
    body: CandidateProjectUpdate,
    current_user: TalentDep,
    service: CandidateServiceDep,
) -> CandidateProjectWithProposalsRead:
    """Update an owned project and return refreshed evidence proposals."""
    owner_id = await service.get_project_owner_id(project_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    project, evidences = await service.update_project(project_id, current_user.id, body)
    return _project_with_evidences(project, list(evidences))


@router.delete(
    "/me/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete one of my projects",
    responses=problem_responses(401, 403, 404),
)
async def delete_project(
    project_id: ProjectIdPath, current_user: TalentDep, service: CandidateServiceDep
) -> None:
    """Delete an owned project."""
    owner_id = await service.get_project_owner_id(project_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    await service.delete_project(project_id, current_user.id)


# ------------------------------------------------------------------------- evidences (S-07)
@router.get(
    "/me/projects/{project_id}/evidences",
    summary="List evidence signals for one of my projects",
    responses=problem_responses(401, 403, 404),
)
async def list_evidences(
    project_id: ProjectIdPath, current_user: TalentDep, service: CandidateServiceDep
) -> list[EvidenceRead]:
    """List reviewable evidence signals for an owned project."""
    owner_id = await service.get_project_owner_id(project_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    evidences = await service.list_evidences(project_id, current_user.id)
    return [EvidenceRead.from_evidence(e) for e in evidences]


@router.patch(
    "/me/projects/{project_id}/evidences/{evidence_id}",
    summary="Review an evidence signal",
    responses=problem_responses(401, 403, 404, 422),
)
async def review_evidence(
    project_id: ProjectIdPath,
    evidence_id: EvidenceIdPath,
    body: EvidenceReviewRequest,
    current_user: TalentDep,
    service: CandidateServiceDep,
) -> EvidenceRead:
    """Confirm, correct, or withdraw an evidence signal and leave an audit trail."""
    owner_id = await service.get_evidence_owner_id(evidence_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    evidence = await service.review_evidence(project_id, evidence_id, current_user.id, body)
    return EvidenceRead.from_evidence(evidence)


@router.get(
    "/me/projects/{project_id}/evidences/{evidence_id}/audit",
    summary="List audit trail for an evidence signal",
    responses=problem_responses(401, 403, 404),
)
async def list_evidence_audit(
    project_id: ProjectIdPath,
    evidence_id: EvidenceIdPath,
    current_user: TalentDep,
    service: CandidateServiceDep,
) -> list[EvidenceAuditRead]:
    """Return the audit trail for an evidence signal."""
    owner_id = await service.get_evidence_owner_id(evidence_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    audits = await service.list_evidence_audits(project_id, evidence_id, current_user.id)
    return [
        EvidenceAuditRead(
            action=a.action,
            from_status=a.from_status,  # type: ignore[arg-type]
            to_status=a.to_status,  # type: ignore[arg-type]
            before=a.before,
            after=a.after,
            created_at=a.created_at,
        )
        for a in audits
    ]


# ------------------------------------------------------------------------ consent
@router.get(
    "/me/consents",
    summary="Read my consent decisions",
    responses=problem_responses(401, 403, 404),
)
async def list_consents(current_user: TalentDep, service: CandidateServiceDep) -> ConsentsRead:
    """Return every purpose with its state; a purpose never decided is reported as denied."""
    consents = await service.list_consents(current_user.id)
    return ConsentsRead.from_consents(consents)


@router.put(
    "/me/consents/{purpose}",
    summary="Grant or withdraw consent for one purpose",
    responses=problem_responses(401, 403, 404, 422),
)
async def set_consent(
    purpose: ConsentPurposePath,
    body: ConsentUpdate,
    current_user: TalentDep,
    service: CandidateServiceDep,
) -> ConsentRead:
    """Set the caller's decision for one purpose.

    Withdrawing ``discovery`` also turns the ``discoverable`` flag off in the same
    transaction, so the profile stops being reachable at once.
    """
    consent = await service.set_consent(current_user.id, purpose, body)
    return ConsentRead(
        purpose=purpose,
        granted=consent.granted,
        granted_at=consent.granted_at,
        revoked_at=consent.revoked_at,
        policy_version=consent.policy_version,
    )


# -------------------------------------------------------------------- projection
@router.get(
    "/{candidate_id}",
    summary="Read a pseudonymised candidate profile",
    responses=problem_responses(401, 403, 404, 422),
    dependencies=[Depends(require_roles(UserRole.EMPRESA))],
    response_model=CandidateProjection,
    response_model_exclude_none=True,
)
async def read_projection(
    candidate_id: CandidateIdPath, service: CandidateServiceDep
) -> dict[str, Any]:
    """Return the pseudonymised profile a company may see (US-15, FR-012).

    The company role is enforced by the endpoint dependency. Only fields the candidate shared
    are present: there is no identity, contact or link field, and a profile that is not shared
    answers ``404``, exactly like one that does not exist.
    """
    return await service.get_projection(candidate_id)
