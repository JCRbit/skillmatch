"""Candidates module models: profile, preferences, visibility flags and declared skills.

The ``users`` table (identity module) says *who can sign in*. ``candidate_profiles`` says *what the
candidate chose to tell us as talent*. The two are linked only by ``candidate_profiles.user_id``;
no identity data (email, password hash, role, status) is duplicated here, and the profile never
stores a real name by default: ``display_name`` is a pseudonym the candidate picks.

Privacy by default: a new profile is not discoverable and does not reveal its location. Granular
consent and the blind-review projection are built on top of these flags by tasks B-05 and B-06.
"""

from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column

from skillmatch.core.database import Base


class WorkMode(StrEnum):
    """How the candidate prefers to work."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class ContractType(StrEnum):
    """Kinds of engagement the candidate is open to."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class SkillLevel(StrEnum):
    """Self-declared proficiency. It is a declaration, not an evaluated level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ConsentPurpose(StrEnum):
    """What the candidate may allow sharing of (US-08, FR-019, decision D-09).

    Every purpose is denied until the candidate grants it explicitly: there is no shared profile
    by default. ``DISCOVERY`` is what lets a company find the pseudonymised profile at all; the
    other two decide which fields that projection may include (built by task B-06).
    """

    DISCOVERY = "discovery"
    LOCATION = "location"
    SKILLS = "skills"


def _utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(UTC)


class CandidateProfile(Base):
    """Talent profile of one user: public-facing data, preferences and visibility flags.

    There is at most one profile per user (unique ``user_id``). Deleting the user deletes the
    profile and its skills; deleting the profile leaves the account untouched.
    """

    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    # --- Profile ---------------------------------------------------------------------------
    display_name: Mapped[str] = mapped_column(String(80), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    languages: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # --- Preferences -----------------------------------------------------------------------
    work_modes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    contract_types: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    preferred_locations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    interests: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # --- Visibility flags (off by default) -------------------------------------------------
    discoverable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    show_location: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )


class CandidateSkill(Base):
    """A skill the candidate declares about themselves.

    ``name`` keeps the text as the candidate wrote it; ``name_key`` is its case-folded form and
    makes a skill unique per candidate regardless of capitalisation. Mapping names to the
    canonical skill taxonomy is a later task and will not change this table's contract.
    """

    __tablename__ = "candidate_skills"
    __table_args__ = (
        UniqueConstraint(
            "candidate_id", "name_key", name="uq_candidate_skills_candidate_id_name_key"
        ),
        CheckConstraint(
            "level IN ('beginner', 'intermediate', 'advanced')",
            name="ck_candidate_skills_level",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    name_key: Mapped[str] = mapped_column(String(60), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )


class ProjectSourceType(StrEnum):
    """Origin of a manually entered project."""

    MANUAL = "manual"
    GITHUB = "github"
    PORTFOLIO = "portfolio"
    OTHER = "other"


class CandidateProject(Base):
    """A project manually entered by a candidate as evidence of experience."""

    __tablename__ = "candidate_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    stack: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ProjectSourceType.MANUAL.value
    )
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    project_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )


class CandidateConsent(Base):
    """One decision of the candidate about one purpose, with its history (US-08, FR-019).

    A row records the *current* state of a purpose: granting and revoking keep the same row and
    move ``granted_at`` / ``revoked_at``, so ``GET`` always reflects the truth and the last
    decision keeps its date. ``policy_version`` is the version of the privacy text the candidate
    saw, so consent can be traced to what was explained at the time.

    There is at most one row per purpose. Absence of a row means "never decided", which is
    treated as not granted: a new profile shares nothing.
    """

    __tablename__ = "candidate_consents"
    __table_args__ = (
        UniqueConstraint(
            "candidate_id", "purpose", name="uq_candidate_consents_candidate_id_purpose"
        ),
        CheckConstraint(
            "purpose IN ('discovery', 'location', 'skills')",
            name="ck_candidate_consents_purpose",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(20), nullable=False)
    granted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    policy_version: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )
