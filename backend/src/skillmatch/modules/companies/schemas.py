"""Schemas for company profile endpoints."""

from datetime import UTC, datetime
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    StringConstraints,
    model_validator,
)

from skillmatch.modules.companies.models import Company


def _collapse_spaces(value: object) -> object:
    return " ".join(value.split()) if isinstance(value, str) else value


def _strip(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


def _to_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


UtcDatetime = Annotated[datetime, AfterValidator(_to_utc)]
Name = Annotated[
    str, BeforeValidator(_collapse_spaces), StringConstraints(min_length=1, max_length=120)
]
Description = Annotated[
    str, BeforeValidator(_strip), StringConstraints(min_length=1, max_length=2000)
]
Website = Annotated[str, BeforeValidator(_strip), StringConstraints(min_length=1, max_length=255)]
Location = Annotated[
    str, BeforeValidator(_collapse_spaces), StringConstraints(min_length=1, max_length=120)
]


class _Request(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CompanyCreate(_Request):
    """Create company request."""

    name: Name
    description: Description | None = None
    website: Website | None = None
    location: Location | None = None


class CompanyUpdate(_Request):
    """Update company request."""

    name: Name | None = None
    description: Description | None = None
    website: Website | None = None
    location: Location | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if not self.model_fields_set:
            msg = "at least one field must be provided"
            raise ValueError(msg)
        if "name" in self.model_fields_set and self.name is None:
            msg = "name must not be null"
            raise ValueError(msg)
        return self


class CompanyRead(BaseModel):
    """Company response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    website: str | None
    location: str | None
    created_at: UtcDatetime
    updated_at: UtcDatetime

    @classmethod
    def from_company(cls, company: Company) -> Self:
        """Build from model."""
        return cls.model_validate(company)
