"""Idempotent seed loader for synthetic SkillMatch datasets.

Loads ``data/synthetic/v1`` into the database tables that currently exist.
The command is safe to run multiple times: it creates missing rows and skips
existing ones without duplicating data.

Currently supported entities:
- users (synthetic TALENTO accounts for candidates)
- candidate_profiles
- candidate_skills

Validated but not persisted yet (no DB models in main):
- companies
- vacancies
- projects
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from skillmatch.core.config import get_settings
from skillmatch.modules.candidates.models import CandidateProfile, CandidateSkill, SkillLevel
from skillmatch.modules.identity.models import ACTIVE_ACCOUNT_STATUS, User, UserRole
from skillmatch.modules.skills import build_alias_index, load_taxonomy

LOGGER = logging.getLogger("skillmatch.seed")

EXPECTED_COUNTS = {"companies": 3, "vacancies": 8, "candidates": 15}
REQUIRED_FILES = [
    "manifest.json",
    "companies.json",
    "vacancies.json",
    "candidates.json",
    "projects.json",
]


@dataclass
class EntityReport:
    """Counts for one seeded entity."""

    created: int = 0
    updated: int = 0
    skipped: int = 0
    pending: int = 0

    def as_dict(self) -> dict[str, int]:
        """Return a JSON-serializable representation."""
        return {
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "pending": self.pending,
        }


@dataclass
class SeedReport:
    """Aggregate report for a seed run."""

    dry_run: bool
    dataset: str
    entities: dict[str, EntityReport] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def entity(self, name: str) -> EntityReport:
        """Get or create an entity report."""
        if name not in self.entities:
            self.entities[name] = EntityReport()
        return self.entities[name]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "dry_run": self.dry_run,
            "dataset": self.dataset,
            "entities": {name: report.as_dict() for name, report in self.entities.items()},
            "warnings": self.warnings,
        }


class SeedValidationError(ValueError):
    """Raised when the dataset is invalid or inconsistent."""


def _load_json(path: Path) -> Any:  # noqa: ANN401 - JSON payload is dynamic
    """Load a JSON file with UTF-8 encoding."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SeedValidationError(f"Missing dataset file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SeedValidationError(f"Invalid JSON in {path}: {exc}") from exc


def load_dataset(dataset_dir: Path) -> dict[str, Any]:
    """Load and minimally validate the synthetic dataset directory."""
    if not dataset_dir.exists() or not dataset_dir.is_dir():
        raise SeedValidationError(f"Dataset directory not found: {dataset_dir}")

    data: dict[str, Any] = {}
    for name in REQUIRED_FILES:
        key = name.replace(".json", "")
        data[key] = _load_json(dataset_dir / name)

    manifest = data["manifest"]
    counts = manifest.get("counts", {})
    for entity, expected in EXPECTED_COUNTS.items():
        actual = counts.get(entity)
        if actual != expected:
            raise SeedValidationError(
                f"Manifest count mismatch for {entity}: expected {expected}, got {actual}"
            )

    companies = data["companies"]
    vacancies = data["vacancies"]
    candidates = data["candidates"]
    projects = data["projects"]

    if len(companies) != EXPECTED_COUNTS["companies"]:
        raise SeedValidationError("companies.json count does not match expected count")
    if len(vacancies) != EXPECTED_COUNTS["vacancies"]:
        raise SeedValidationError("vacancies.json count does not match expected count")
    if len(candidates) != EXPECTED_COUNTS["candidates"]:
        raise SeedValidationError("candidates.json count does not match expected count")

    company_ids = {c["company_id"] for c in companies}
    for vacancy in vacancies:
        if vacancy["company_id"] not in company_ids:
            raise SeedValidationError(
                f"Vacancy {vacancy.get('vacancy_id')} references unknown company"
            )

    project_ids = {p["project_id"] for p in projects}
    candidate_ids = {c["candidate_id"] for c in candidates}
    for project in projects:
        if project["candidate_id"] not in candidate_ids:
            raise SeedValidationError(
                f"Project {project.get('project_id')} references unknown candidate"
            )
    for candidate in candidates:
        for project_id in candidate.get("project_ids", []):
            if project_id not in project_ids:
                raise SeedValidationError(
                    f"Candidate {candidate.get('candidate_id')} references unknown project"
                )

    # Validate skill canonical IDs against taxonomy
    taxonomy = load_taxonomy()
    canonical_ids = {skill.canonical_id for skill in taxonomy}
    # Also build alias index to ensure taxonomy is internally consistent
    build_alias_index(taxonomy)

    for candidate in candidates:
        for skill in candidate.get("skills", []):
            canonical_id = skill.get("canonical_id")
            if canonical_id not in canonical_ids:
                raise SeedValidationError(
                    f"Candidate {candidate.get('candidate_id')} has unknown canonical skill: "
                    f"{canonical_id}"
                )
    for vacancy in vacancies:
        for skill_id in vacancy.get("essential_skills", []) + vacancy.get("desirable_skills", []):
            if skill_id not in canonical_ids:
                raise SeedValidationError(
                    f"Vacancy {vacancy.get('vacancy_id')} has unknown canonical skill: {skill_id}"
                )

    return data


def _normalize_skill_name(value: str) -> str:
    """Normalize skill name for the current CandidateSkill.name_key field."""
    return " ".join(value.strip().casefold().split())


def _map_skill_level(value: str) -> str:
    """Map dataset declared_level to the DB enum value."""
    try:
        return SkillLevel(value).value
    except ValueError as exc:
        raise SeedValidationError(f"Unsupported skill level: {value}") from exc


async def _ensure_user(
    session: AsyncSession, candidate: dict[str, Any], report: SeedReport
) -> User:
    """Create or reuse a synthetic user for a candidate."""
    email = candidate["email"].strip().lower()
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        report.entity("users").skipped += 1
        return user

    user = User(
        email=email,
        password_hash=None,  # synthetic seed account; not usable for password login
        role=UserRole.TALENTO,
        status=ACTIVE_ACCOUNT_STATUS,
    )
    session.add(user)
    await session.flush()
    report.entity("users").created += 1
    return user


async def _ensure_profile(
    session: AsyncSession, user: User, candidate: dict[str, Any], report: SeedReport
) -> CandidateProfile:
    """Create or reuse a candidate profile for a user."""
    result = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is not None:
        report.entity("candidate_profiles").skipped += 1
        return profile

    languages = [
        lang.get("language") for lang in candidate.get("languages", []) if lang.get("language")
    ]
    profile = CandidateProfile(
        user_id=user.id,
        display_name=candidate["display_name"],
        summary=candidate.get("summary"),
        city=candidate.get("location"),
        languages=languages,
        work_modes=[candidate["modality_preference"]]
        if candidate.get("modality_preference")
        else [],
        contract_types=[],
        preferred_locations=[candidate["location"]] if candidate.get("location") else [],
        interests=[],
        discoverable=candidate.get("visibility") == "public",
        show_location=False,
    )
    session.add(profile)
    await session.flush()
    report.entity("candidate_profiles").created += 1
    return profile


async def _ensure_skills(
    session: AsyncSession,
    profile: CandidateProfile,
    candidate: dict[str, Any],
    report: SeedReport,
) -> None:
    """Create missing skills for a profile; never duplicate name_key."""
    existing_result = await session.execute(
        select(CandidateSkill).where(CandidateSkill.candidate_id == profile.id)
    )
    existing = {skill.name_key: skill for skill in existing_result.scalars().all()}

    for skill_data in candidate.get("skills", []):
        raw_name = str(skill_data.get("observed_raw_term") or skill_data.get("canonical_id"))
        name_key = _normalize_skill_name(raw_name)
        if not name_key:
            raise SeedValidationError(
                f"Candidate {candidate.get('candidate_id')} has empty skill name"
            )
        if name_key in existing:
            report.entity("candidate_skills").skipped += 1
            continue

        skill = CandidateSkill(
            candidate_id=profile.id,
            name=raw_name.strip(),
            name_key=name_key,
            level=_map_skill_level(str(skill_data.get("declared_level", "beginner"))),
        )
        session.add(skill)
        existing[name_key] = skill
        report.entity("candidate_skills").created += 1


async def seed_dataset(
    dataset_dir: Path,
    *,
    session_factory: async_sessionmaker[AsyncSession],
    dry_run: bool = False,
) -> SeedReport:
    """Seed the dataset into the database idempotently."""
    data = load_dataset(dataset_dir)
    report = SeedReport(dry_run=dry_run, dataset=str(dataset_dir))

    report.entity("companies").pending += len(data["companies"])
    report.entity("vacancies").pending += len(data["vacancies"])
    report.entity("projects").pending += len(data["projects"])
    report.warnings.append(
        "companies, vacancies and projects are validated but not persisted: "
        "no DB models in main yet"
    )

    async with session_factory() as session:
        for candidate in data["candidates"]:
            user = await _ensure_user(session, candidate, report)
            profile = await _ensure_profile(session, user, candidate, report)
            await _ensure_skills(session, profile, candidate, report)

        if dry_run:
            await session.rollback()
        else:
            await session.commit()

    return report


async def _run(args: argparse.Namespace) -> int:
    """Execute the seed command."""
    dataset_dir = Path(args.dataset)
    settings = get_settings()
    database_url = args.database_url or settings.database_url

    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        report = await seed_dataset(
            dataset_dir, session_factory=session_factory, dry_run=args.dry_run
        )
    finally:
        await engine.dispose()

    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))  # noqa: T201
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Load SkillMatch synthetic seed dataset idempotently."
    )
    parser.add_argument(
        "--dataset",
        default="data/synthetic/v1",
        help="Path to synthetic dataset directory (default: data/synthetic/v1)",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Database URL override. Defaults to SKILLMATCH_DATABASE_URL/settings.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and compute changes, but rollback instead of committing.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except SeedValidationError as exc:
        LOGGER.error("Seed validation failed: %s", exc)
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))  # noqa: T201
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
