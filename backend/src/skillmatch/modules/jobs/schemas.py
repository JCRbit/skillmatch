"""Schemas for vacancy endpoints."""

from datetime import UTC, datetime
from typing import Annotated, Any, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from skillmatch.modules.jobs.models import ContractType, Seniority, Vacancy, VacancyStatus, WorkMode


def _collapse_spaces(value: object) -> object:
    return " ".join(value.split()) if isinstance(value, str) else value


def _strip(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


def _no_duplicates(values: list[Any]) -> list[Any]:
    keys = [str(item).casefold() for item in values]
    if len(keys) != len(set(keys)):
        msg = "items must not repeat"
        raise ValueError(msg)
    return values


def _to_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


UtcDatetime = Annotated[datetime, AfterValidator(_to_utc)]
Title = Annotated[
    str, BeforeValidator(_collapse_spaces), StringConstraints(min_length=1, max_length=120)
]
Description = Annotated[
    str, BeforeValidator(_strip), StringConstraints(min_length=1, max_length=5000)
]
Location = Annotated[
    str, BeforeValidator(_collapse_spaces), StringConstraints(min_length=1, max_length=120)
]
SkillName = Annotated[
    str, BeforeValidator(_collapse_spaces), StringConstraints(min_length=1, max_length=60)
]
SkillList = Annotated[list[SkillName], Field(max_length=50), AfterValidator(_no_duplicates)]


class _Request(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VacancyCreate(_Request):
    """Create vacancy request."""

    title: Title
    description: Description
    seniority: Seniority
    location: Location | None = None
    work_mode: WorkMode
    contract_type: ContractType
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")] | None = None
    essential_skills: SkillList = Field(default_factory=list)
    desirable_skills: SkillList = Field(default_factory=list)
    status: VacancyStatus = VacancyStatus.DRAFT

    @model_validator(mode="after")
    def _validate_salary(self) -> Self:
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            msg = "salary_min must be <= salary_max"
            raise ValueError(msg)
        if (
            self.salary_min is not None or self.salary_max is not None
        ) and self.salary_currency is None:
            msg = "salary_currency is required when salary is provided"
            raise ValueError(msg)
        return self


class VacancyUpdate(_Request):
    """Update vacancy request."""

    title: Title | None = None
    description: Description | None = None
    seniority: Seniority | None = None
    location: Location | None = None
    work_mode: WorkMode | None = None
    contract_type: ContractType | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")] | None = None
    essential_skills: SkillList | None = None
    desirable_skills: SkillList | None = None
    status: VacancyStatus | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if not self.model_fields_set:
            msg = "at least one field must be provided"
            raise ValueError(msg)
        non_nullable = [
            "title",
            "description",
            "seniority",
            "work_mode",
            "contract_type",
            "essential_skills",
            "desirable_skills",
            "status",
        ]
        for field in non_nullable:
            if field in self.model_fields_set and getattr(self, field) is None:
                msg = f"{field} must not be null"
                raise ValueError(msg)
        if (
            "salary_min" in self.model_fields_set
            and "salary_max" in self.model_fields_set
            and self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            msg = "salary_min must be <= salary_max"
            raise ValueError(msg)
        return self


class VacancyRead(BaseModel):
    """Vacancy response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    title: str
    description: str
    seniority: Seniority
    location: str | None
    work_mode: WorkMode
    contract_type: ContractType
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    essential_skills: list[str]
    desirable_skills: list[str]
    status: VacancyStatus
    created_at: UtcDatetime
    updated_at: UtcDatetime

    @classmethod
    def from_vacancy(cls, vacancy: Vacancy) -> Self:
        """Build from model."""
        return cls(
            id=vacancy.id,
            company_id=vacancy.company_id,
            title=vacancy.title,
            description=vacancy.description,
            seniority=Seniority(vacancy.seniority),
            location=vacancy.location,
            work_mode=WorkMode(vacancy.work_mode),
            contract_type=ContractType(vacancy.contract_type),
            salary_min=vacancy.salary_min,
            salary_max=vacancy.salary_max,
            salary_currency=vacancy.salary_currency,
            essential_skills=list(vacancy.essential_skills),
            desirable_skills=list(vacancy.desirable_skills),
            status=VacancyStatus(vacancy.status),
            created_at=vacancy.created_at,
            updated_at=vacancy.updated_at,
        )
