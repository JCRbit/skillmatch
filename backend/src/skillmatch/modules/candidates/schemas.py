"""Request and response models of the candidate endpoints.

Requests forbid unknown fields, so a client can never smuggle in ``user_id``, ``id`` or any other
value that is not part of the contract: the owner of a profile is always the authenticated user.
Validation errors never echo the submitted values (see :mod:`skillmatch.core.errors`), which
matters because these bodies carry personal data.
"""

import re
from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Annotated, Any, Final, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictBool,
    StringConstraints,
    model_validator,
)

from skillmatch.modules.candidates.models import (
    CandidateConsent,
    CandidateProfile,
    CandidateProject,
    CandidateProjectEvidence,
    CandidateSkill,
    ConsentPurpose,
    ContractType,
    EvidenceStatus,
    ProjectSourceType,
    SkillLevel,
    WorkMode,
)

DISPLAY_NAME_MAX_LENGTH: Final = 80
SUMMARY_MAX_LENGTH: Final = 2000
CITY_MAX_LENGTH: Final = 100
MAX_LANGUAGES: Final = 10
MAX_PREFERRED_LOCATIONS: Final = 10
MAX_INTERESTS: Final = 20
POLICY_VERSION_MAX_LENGTH: Final = 20
SKILL_NAME_MAX_LENGTH: Final = 60

_SKILL_NAME_PATTERN: Final = re.compile(r"[\w.][\w .+#/&()-]*")
"""Letters, digits and the punctuation of real skill names (``C++``, ``.NET``, ``CI/CD``)."""


# --------------------------------------------------------------------------- #
# Reusable field types
# --------------------------------------------------------------------------- #
def _collapse_spaces(value: object) -> object:
    """Trim a string and collapse every run of whitespace into one space."""
    return " ".join(value.split()) if isinstance(value, str) else value


def _strip(value: object) -> object:
    """Trim a string, keeping inner line breaks."""
    return value.strip() if isinstance(value, str) else value


def _normalise_language(value: object) -> object:
    """Trim and lower-case a language code."""
    return value.strip().lower() if isinstance(value, str) else value


def _no_duplicates(values: list[Any]) -> list[Any]:
    """Reject a list that repeats an item (case-insensitively)."""
    keys = [str(item).casefold() for item in values]
    if len(keys) != len(set(keys)):
        msg = "items must not repeat"
        raise ValueError(msg)
    return values


def _check_skill_name(value: str) -> str:
    """Accept only the characters that real skill names use."""
    if _SKILL_NAME_PATTERN.fullmatch(value) is None or not any(
        character.isalnum() for character in value
    ):
        msg = "skill name contains unsupported characters"
        raise ValueError(msg)
    return value


def _to_utc(value: datetime) -> datetime:
    """Treat naive database timestamps as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


UtcDatetime = Annotated[datetime, AfterValidator(_to_utc)]
"""A timezone-aware UTC timestamp."""

DisplayName = Annotated[
    str,
    BeforeValidator(_collapse_spaces),
    StringConstraints(min_length=1, max_length=DISPLAY_NAME_MAX_LENGTH),
]
Summary = Annotated[
    str,
    BeforeValidator(_strip),
    StringConstraints(min_length=1, max_length=SUMMARY_MAX_LENGTH),
]
City = Annotated[
    str,
    BeforeValidator(_collapse_spaces),
    StringConstraints(min_length=1, max_length=CITY_MAX_LENGTH),
]
LanguageCode = Annotated[
    str,
    BeforeValidator(_normalise_language),
    StringConstraints(pattern=r"^[a-z]{2,3}$"),
]
Languages = Annotated[
    list[LanguageCode], Field(max_length=MAX_LANGUAGES), AfterValidator(_no_duplicates)
]
PlaceName = Annotated[
    str,
    BeforeValidator(_collapse_spaces),
    StringConstraints(min_length=1, max_length=CITY_MAX_LENGTH),
]
Interest = Annotated[
    str,
    BeforeValidator(_collapse_spaces),
    StringConstraints(min_length=1, max_length=SKILL_NAME_MAX_LENGTH),
]
SkillName = Annotated[
    str,
    BeforeValidator(_collapse_spaces),
    StringConstraints(min_length=1, max_length=SKILL_NAME_MAX_LENGTH),
    AfterValidator(_check_skill_name),
]


class _Request(BaseModel):
    """Base of every request body: unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #
class CandidateProfileCreate(_Request):
    """Body of ``POST /candidates/me``.

    Preferences and visibility are not part of creation: a new profile starts private and with
    empty preferences, and the candidate opts in through their own endpoints.
    """

    display_name: DisplayName = Field(description="Pseudonym shown instead of a real name.")
    summary: Summary | None = None
    city: City | None = None
    languages: Languages = Field(
        default_factory=list, description="Lower-case ISO 639 codes, e.g. `es`, `en`."
    )


class CandidateProfileUpdate(_Request):
    """Body of ``PATCH /candidates/me``: only the fields sent are changed.

    ``summary`` and ``city`` accept ``null`` to clear them; ``display_name`` and ``languages``
    cannot be null (send ``[]`` to clear the languages).
    """

    display_name: DisplayName | None = None
    summary: Summary | None = None
    city: City | None = None
    languages: Languages | None = None

    @model_validator(mode="after")
    def _at_least_one_valid_field(self) -> Self:
        """Require a change and refuse null for the fields that cannot be cleared."""
        if not self.model_fields_set:
            msg = "at least one field must be provided"
            raise ValueError(msg)
        for name in ("display_name", "languages"):
            if name in self.model_fields_set and getattr(self, name) is None:
                msg = f"{name} must not be null"
                raise ValueError(msg)
        return self


# --------------------------------------------------------------------------- #
# Preferences and visibility
# --------------------------------------------------------------------------- #
class PreferencesUpdate(_Request):
    """Body of ``PUT /candidates/me/preferences``: replaces every preference.

    Every field is required (an empty list means "no preference") so a client can never wipe
    the preferences by omitting a field.
    """

    work_modes: Annotated[
        list[WorkMode], Field(max_length=len(WorkMode)), AfterValidator(_no_duplicates)
    ]
    contract_types: Annotated[
        list[ContractType], Field(max_length=len(ContractType)), AfterValidator(_no_duplicates)
    ]
    preferred_locations: Annotated[
        list[PlaceName], Field(max_length=MAX_PREFERRED_LOCATIONS), AfterValidator(_no_duplicates)
    ]
    interests: Annotated[
        list[Interest], Field(max_length=MAX_INTERESTS), AfterValidator(_no_duplicates)
    ]


class PreferencesRead(BaseModel):
    """The candidate's preferences."""

    model_config = ConfigDict(from_attributes=True)

    work_modes: list[WorkMode]
    contract_types: list[ContractType]
    preferred_locations: list[str]
    interests: list[str]


class VisibilityUpdate(_Request):
    """Body of ``PUT /candidates/me/visibility``: both flags are explicit, never defaulted."""

    discoverable: StrictBool = Field(
        description="Whether companies may find a pseudonymised version of this profile."
    )
    show_location: StrictBool = Field(
        description="Whether the city may be part of the pseudonymised version."
    )


class VisibilityRead(BaseModel):
    """The candidate's visibility flags."""

    model_config = ConfigDict(from_attributes=True)

    discoverable: bool
    show_location: bool


class CandidateProfileRead(BaseModel):
    """The candidate's own profile. It never includes identity data (email, role, ids)."""

    display_name: str
    summary: str | None
    city: str | None
    languages: list[str]
    preferences: PreferencesRead
    visibility: VisibilityRead
    created_at: UtcDatetime
    updated_at: UtcDatetime

    @classmethod
    def from_profile(cls, profile: CandidateProfile) -> Self:
        """Build the representation of a stored profile."""
        return cls(
            display_name=profile.display_name,
            summary=profile.summary,
            city=profile.city,
            languages=list(profile.languages),
            preferences=PreferencesRead.model_validate(profile),
            visibility=VisibilityRead.model_validate(profile),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )


# --------------------------------------------------------------------------- #
# Skills
# --------------------------------------------------------------------------- #
class SkillCreate(_Request):
    """Body of ``POST /candidates/me/skills``."""

    name: SkillName = Field(description="Skill as the candidate names it, e.g. `Python`.")
    level: SkillLevel = Field(description="Self-declared proficiency.")


class SkillUpdate(_Request):
    """Body of ``PATCH /candidates/me/skills/{skill_id}``: only the fields sent are changed."""

    name: SkillName | None = None
    level: SkillLevel | None = None

    @model_validator(mode="after")
    def _at_least_one_valid_field(self) -> Self:
        """Require a change and refuse null values."""
        if not self.model_fields_set:
            msg = "at least one field must be provided"
            raise ValueError(msg)
        if any(getattr(self, name) is None for name in self.model_fields_set):
            msg = "fields must not be null"
            raise ValueError(msg)
        return self


class SkillRead(BaseModel):
    """A skill declared by the candidate."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    level: SkillLevel
    created_at: UtcDatetime
    updated_at: UtcDatetime

    @classmethod
    def from_skill(cls, skill: CandidateSkill) -> Self:
        """Build the representation of a stored skill."""
        return cls.model_validate(skill)


# --------------------------------------------------------------------------- #
# Projects / evidence proposals (S-06)
# --------------------------------------------------------------------------- #
PROJECT_NAME_MAX_LENGTH: Final = 120
PROJECT_ROLE_MAX_LENGTH: Final = 120
PROJECT_DESCRIPTION_MAX_LENGTH: Final = 5000
PROJECT_URL_MAX_LENGTH: Final = 500
MAX_PROJECT_STACK_ITEMS: Final = 30


class EvidenceProposalRead(BaseModel):
    """A skill proposal extracted from project text against the local taxonomy."""

    canonical_id: str
    skill: str
    matched_term: str
    source: str = Field(
        description="Where the term was matched: name, description, role, or stack."
    )


class EvidenceAuditRead(BaseModel):
    """Audit record for an evidence review action."""

    action: str
    from_status: EvidenceStatus
    to_status: EvidenceStatus
    before: dict[str, Any]
    after: dict[str, Any]
    created_at: UtcDatetime


class EvidenceRead(BaseModel):
    """A reviewable evidence signal for a project."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    canonical_id: str
    skill_label: str
    matched_term: str
    source: str
    status: EvidenceStatus
    note: str | None
    created_at: UtcDatetime
    updated_at: UtcDatetime

    @classmethod
    def from_evidence(cls, evidence: CandidateProjectEvidence) -> Self:
        """Build representation from stored evidence."""
        return cls.model_validate(evidence)


class EvidenceReviewRequest(_Request):
    """Body of ``PATCH /candidates/me/projects/{project_id}/evidences/{evidence_id}``."""

    action: Literal["confirm", "correct", "withdraw"] = Field(
        description="Review action: confirm, correct, or withdraw the evidence."
    )
    canonical_id: (
        Annotated[
            str,
            BeforeValidator(_collapse_spaces),
            StringConstraints(min_length=1, max_length=120),
        ]
        | None
    ) = None
    skill_label: (
        Annotated[
            str,
            BeforeValidator(_collapse_spaces),
            StringConstraints(min_length=1, max_length=120),
        ]
        | None
    ) = None
    matched_term: (
        Annotated[
            str,
            BeforeValidator(_collapse_spaces),
            StringConstraints(min_length=1, max_length=120),
        ]
        | None
    ) = None
    note: (
        Annotated[
            str,
            BeforeValidator(_strip),
            StringConstraints(min_length=1, max_length=500),
        ]
        | None
    ) = None

    @model_validator(mode="after")
    def _validate_action(self) -> Self:
        if self.action == "correct":
            if not any(
                value is not None
                for value in (self.canonical_id, self.skill_label, self.matched_term, self.note)
            ):
                msg = "correct action requires at least one correction field"
                raise ValueError(msg)
        else:
            disallowed = {
                name
                for name in ("canonical_id", "skill_label", "matched_term")
                if getattr(self, name) is not None
            }
            if disallowed:
                msg = f"{', '.join(sorted(disallowed))} only allowed for correct action"
                raise ValueError(msg)
        return self


class CandidateProjectCreate(_Request):
    """Body of ``POST /candidates/me/projects``."""

    name: Annotated[
        str,
        BeforeValidator(_collapse_spaces),
        StringConstraints(min_length=1, max_length=PROJECT_NAME_MAX_LENGTH),
    ]
    description: Annotated[
        str,
        BeforeValidator(_strip),
        StringConstraints(min_length=1, max_length=PROJECT_DESCRIPTION_MAX_LENGTH),
    ]
    role: Annotated[
        str,
        BeforeValidator(_collapse_spaces),
        StringConstraints(min_length=1, max_length=PROJECT_ROLE_MAX_LENGTH),
    ]
    stack: Annotated[
        list[
            Annotated[
                str,
                BeforeValidator(_collapse_spaces),
                StringConstraints(min_length=1, max_length=SKILL_NAME_MAX_LENGTH),
            ]
        ],
        Field(max_length=MAX_PROJECT_STACK_ITEMS),
        AfterValidator(_no_duplicates),
    ] = Field(default_factory=list)
    source_type: ProjectSourceType = ProjectSourceType.MANUAL
    source_url: (
        Annotated[
            str,
            BeforeValidator(_strip),
            StringConstraints(min_length=1, max_length=PROJECT_URL_MAX_LENGTH),
        ]
        | None
    ) = None
    project_date: date


class CandidateProjectUpdate(_Request):
    """Body of ``PATCH /candidates/me/projects/{project_id}``."""

    name: (
        Annotated[
            str,
            BeforeValidator(_collapse_spaces),
            StringConstraints(min_length=1, max_length=PROJECT_NAME_MAX_LENGTH),
        ]
        | None
    ) = None
    description: (
        Annotated[
            str,
            BeforeValidator(_strip),
            StringConstraints(min_length=1, max_length=PROJECT_DESCRIPTION_MAX_LENGTH),
        ]
        | None
    ) = None
    role: (
        Annotated[
            str,
            BeforeValidator(_collapse_spaces),
            StringConstraints(min_length=1, max_length=PROJECT_ROLE_MAX_LENGTH),
        ]
        | None
    ) = None
    stack: (
        Annotated[
            list[
                Annotated[
                    str,
                    BeforeValidator(_collapse_spaces),
                    StringConstraints(min_length=1, max_length=SKILL_NAME_MAX_LENGTH),
                ]
            ],
            Field(max_length=MAX_PROJECT_STACK_ITEMS),
            AfterValidator(_no_duplicates),
        ]
        | None
    ) = None
    source_type: ProjectSourceType | None = None
    source_url: (
        Annotated[
            str,
            BeforeValidator(_strip),
            StringConstraints(min_length=1, max_length=PROJECT_URL_MAX_LENGTH),
        ]
        | None
    ) = None
    project_date: date | None = None

    @model_validator(mode="after")
    def _at_least_one_valid_field(self) -> Self:
        if not self.model_fields_set:
            msg = "at least one field must be provided"
            raise ValueError(msg)
        return self


class CandidateProjectRead(BaseModel):
    """A manually entered project."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    role: str
    stack: list[str]
    source_type: ProjectSourceType
    source_url: str | None
    project_date: date
    created_at: UtcDatetime
    updated_at: UtcDatetime

    @classmethod
    def from_project(cls, project: CandidateProject) -> Self:
        """Build the representation of a stored project."""
        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            role=project.role,
            stack=list(project.stack),
            source_type=ProjectSourceType(project.source_type),
            source_url=project.source_url,
            project_date=project.project_date,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )


class CandidateProjectWithProposalsRead(CandidateProjectRead):
    """Project with evidence proposals derived from text."""

    evidence_proposals: list[EvidenceProposalRead] = Field(default_factory=list)
    evidences: list[EvidenceRead] = Field(default_factory=list)


# Consent
# --------------------------------------------------------------------------- #
class ConsentUpdate(_Request):
    """Body of ``PUT /candidates/me/consents/{purpose}``: the candidate's decision.

    ``granted`` is required and strict: there is no default, so a client can never grant or
    revoke a purpose by accident. ``policy_version`` is optional; when it is omitted the server
    records the version of the privacy text it currently publishes.
    """

    granted: StrictBool = Field(
        description="True to allow sharing for this purpose, false to withdraw it."
    )
    policy_version: (
        Annotated[
            str,
            BeforeValidator(_strip),
            StringConstraints(min_length=1, max_length=POLICY_VERSION_MAX_LENGTH),
        ]
        | None
    ) = None


class ConsentRead(BaseModel):
    """The state of one purpose. A purpose never decided is reported as not granted."""

    purpose: ConsentPurpose
    granted: bool
    granted_at: UtcDatetime | None
    revoked_at: UtcDatetime | None
    policy_version: str | None


class ConsentsRead(BaseModel):
    """Every purpose, always present, so a client never has to guess a missing one."""

    consents: list[ConsentRead]

    @classmethod
    def from_consents(cls, stored: Sequence[CandidateConsent]) -> Self:
        """Build the full list, filling in the purposes that were never decided."""
        by_purpose = {consent.purpose: consent for consent in stored}
        return cls(
            consents=[
                ConsentRead(
                    purpose=purpose,
                    granted=consent.granted,
                    granted_at=consent.granted_at,
                    revoked_at=consent.revoked_at,
                    policy_version=consent.policy_version,
                )
                if consent is not None
                else ConsentRead(
                    purpose=purpose,
                    granted=False,
                    granted_at=None,
                    revoked_at=None,
                    policy_version=None,
                )
                for purpose in ConsentPurpose
                for consent in (by_purpose.get(purpose.value),)
            ]
        )
