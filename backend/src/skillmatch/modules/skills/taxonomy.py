"""Load and validate the S-01 skills taxonomy."""

import csv
from dataclasses import dataclass
from importlib import resources

EXPECTED_COLUMNS = (
    "category_id",
    "category",
    "canonical_id",
    "skill",
    "aliases",
    "operational_description",
    "esco_label",
    "esco_uri",
    "esco_concept_type",
    "esco_concept_state",
    "esco_status",
)


class TaxonomyError(ValueError):
    """Raised when the skills taxonomy is invalid."""


def _optional_value(record: dict[str, str], field: str) -> str | None:
    """Return a stripped CSV value or None when it is empty."""
    value = record[field].strip()
    return value or None


@dataclass(frozen=True)
class Skill:
    """Represent a canonical skill in the taxonomy."""

    category_id: str
    category: str
    canonical_id: str
    skill: str
    aliases: tuple[str, ...]
    operational_description: str
    esco_label: str | None
    esco_uri: str | None
    esco_concept_type: str | None
    esco_concept_state: str | None
    esco_status: str


def load_taxonomy() -> tuple[Skill, ...]:
    """Load the packaged CSV taxonomy and validate its structure."""
    resource = resources.files("skillmatch.modules.skills").joinpath("data", "skills_v1.csv")

    with resource.open("r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        headers = next(reader, None)

        if tuple(headers or ()) != EXPECTED_COLUMNS:
            raise TaxonomyError("The taxonomy CSV has an invalid header.")

        skills: list[Skill] = []
        canonical_ids: set[str] = set()

        for row_number, values in enumerate(reader, start=2):
            if len(values) != len(EXPECTED_COLUMNS):
                raise TaxonomyError(f"Invalid number of columns at CSV row {row_number}.")

            record = dict(zip(EXPECTED_COLUMNS, values, strict=True))

            required_fields = (
                "category_id",
                "category",
                "canonical_id",
                "skill",
                "operational_description",
                "esco_status",
            )

            for field in required_fields:
                if not record[field].strip():
                    raise TaxonomyError(
                        f"Missing required field '{field}' at CSV row {row_number}."
                    )

            canonical_id = record["canonical_id"].strip()

            if canonical_id in canonical_ids:
                raise TaxonomyError(
                    f"Duplicate canonical_id '{canonical_id}' at CSV row {row_number}."
                )

            canonical_ids.add(canonical_id)

            aliases = tuple(
                alias.strip() for alias in record["aliases"].split(";") if alias.strip()
            )

            skills.append(
                Skill(
                    category_id=record["category_id"].strip(),
                    category=record["category"].strip(),
                    canonical_id=canonical_id,
                    skill=record["skill"].strip(),
                    aliases=aliases,
                    operational_description=record["operational_description"].strip(),
                    esco_label=_optional_value(record, "esco_label"),
                    esco_uri=_optional_value(record, "esco_uri"),
                    esco_concept_type=_optional_value(record, "esco_concept_type"),
                    esco_concept_state=_optional_value(record, "esco_concept_state"),
                    esco_status=record["esco_status"].strip(),
                )
            )

    return tuple(skills)
