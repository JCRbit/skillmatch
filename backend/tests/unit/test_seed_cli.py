import asyncio
import json
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from skillmatch.cli.seed import SeedValidationError, load_dataset, seed_dataset
from skillmatch.core.database import Base
from skillmatch.modules.candidates.models import CandidateProfile, CandidateSkill
from skillmatch.modules.identity.models import ACTIVE_ACCOUNT_STATUS, User, UserRole


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _dataset_dir() -> Path:
    return _repo_root() / "data" / "synthetic" / "v1"


def _make_session_factory() -> tuple[async_sessionmaker[AsyncSession], AsyncEngine]:
    engine = create_async_engine("sqlite+aiosqlite://")

    async def _create() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())
    return async_sessionmaker(engine, expire_on_commit=False), engine


def test_load_dataset_validates_counts_and_refs() -> None:
    data = load_dataset(_dataset_dir())
    assert len(data["companies"]) == 3
    assert len(data["vacancies"]) == 8
    assert len(data["candidates"]) == 15
    assert len(data["projects"]) >= 15


def test_seed_dataset_is_idempotent() -> None:
    session_factory, engine = _make_session_factory()
    try:
        dataset = _dataset_dir()
        report1 = asyncio.run(seed_dataset(dataset, session_factory=session_factory, dry_run=False))
        report2 = asyncio.run(seed_dataset(dataset, session_factory=session_factory, dry_run=False))

        assert report1.entities["users"].created == 15
        assert report1.entities["candidate_profiles"].created == 15
        assert report1.entities["candidate_skills"].created > 0

        assert report2.entities["users"].created == 0
        assert report2.entities["candidate_profiles"].created == 0
        assert report2.entities["candidate_skills"].created == 0
        assert report2.entities["users"].skipped == 15

        async def _counts() -> tuple[int, int, int]:
            async with session_factory() as session:
                users = (await session.execute(select(func.count()).select_from(User))).scalar_one()
                profiles = (
                    await session.execute(select(func.count()).select_from(CandidateProfile))
                ).scalar_one()
                skills = (
                    await session.execute(select(func.count()).select_from(CandidateSkill))
                ).scalar_one()
                return users, profiles, skills

        users, profiles, skills = asyncio.run(_counts())
        assert users == 15
        assert profiles == 15
        assert skills == report1.entities["candidate_skills"].created
    finally:
        asyncio.run(engine.dispose())


def test_seed_dataset_dry_run_does_not_persist() -> None:
    session_factory, engine = _make_session_factory()
    try:
        report = asyncio.run(
            seed_dataset(_dataset_dir(), session_factory=session_factory, dry_run=True)
        )
        assert report.dry_run is True
        assert report.entities["users"].created == 15

        async def _count_users() -> int:
            async with session_factory() as session:
                return (await session.execute(select(func.count()).select_from(User))).scalar_one()

        assert asyncio.run(_count_users()) == 0
    finally:
        asyncio.run(engine.dispose())


def test_load_dataset_rejects_bad_skill(tmp_path: Path) -> None:
    dataset = tmp_path / "v1"
    dataset.mkdir()
    src = _dataset_dir()
    for f in src.glob("*.json"):
        dataset.joinpath(f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    candidates = json.loads((dataset / "candidates.json").read_text(encoding="utf-8"))
    candidates[0]["skills"][0]["canonical_id"] = "not-a-real-skill"
    (dataset / "candidates.json").write_text(json.dumps(candidates), encoding="utf-8")

    with pytest.raises(SeedValidationError):
        load_dataset(dataset)


def test_seed_dataset_rejects_existing_user_with_incompatible_role() -> None:
    session_factory, engine = _make_session_factory()
    try:
        dataset = _dataset_dir()
        data = load_dataset(dataset)
        email = data["candidates"][0]["email"].strip().lower()

        async def _insert_conflicting_user() -> None:
            async with session_factory() as session:
                session.add(
                    User(
                        email=email,
                        password_hash="hashed",  # noqa: S106 - test fixture, not real secret
                        role=UserRole.EMPRESA,
                        status=ACTIVE_ACCOUNT_STATUS,
                    )
                )
                await session.commit()

        asyncio.run(_insert_conflicting_user())

        with pytest.raises(SeedValidationError, match="incompatible role"):
            asyncio.run(seed_dataset(dataset, session_factory=session_factory, dry_run=False))

        async def _counts() -> tuple[int, int, int]:
            async with session_factory() as session:
                users = (await session.execute(select(func.count()).select_from(User))).scalar_one()
                profiles = (
                    await session.execute(select(func.count()).select_from(CandidateProfile))
                ).scalar_one()
                skills = (
                    await session.execute(select(func.count()).select_from(CandidateSkill))
                ).scalar_one()
                return users, profiles, skills

        users, profiles, skills = asyncio.run(_counts())
        assert users == 1
        assert profiles == 0
        assert skills == 0
    finally:
        asyncio.run(engine.dispose())


def test_load_dataset_rejects_malformed_structure(tmp_path: Path) -> None:
    dataset = tmp_path / "v1"
    dataset.mkdir()
    src = _dataset_dir()
    for f in src.glob("*.json"):
        dataset.joinpath(f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    # malformed: candidates is not a list of candidate dicts
    (dataset / "candidates.json").write_text(json.dumps({"bad": True}), encoding="utf-8")

    with pytest.raises(SeedValidationError):
        load_dataset(dataset)
