"""Vacancy model.

Vacancies belong to a company. Essential and desirable skills are separated from
objective conditions (seniority, location, work mode, contract type, salary).
"""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from skillmatch.core.database import Base


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Seniority(StrEnum):
    """Vacancy seniority."""

    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class WorkMode(StrEnum):
    """Vacancy work mode."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class ContractType(StrEnum):
    """Vacancy contract type."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class VacancyStatus(StrEnum):
    """Vacancy status."""

    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


class Vacancy(Base):
    """A job vacancy owned by a company."""

    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    seniority: Mapped[str] = mapped_column(String(20), nullable=False)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    work_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(20), nullable=False)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    essential_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    desirable_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=VacancyStatus.DRAFT.value
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )
