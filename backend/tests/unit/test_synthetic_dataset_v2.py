import json
from datetime import date
from pathlib import Path
from typing import Any

from skillmatch.modules.skills import load_taxonomy


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load(name: str) -> Any:  # noqa: ANN401 - JSON dataset payload is dynamic
    path = _repo_root() / "data" / "synthetic" / "v2" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_synthetic_dataset_v2_counts() -> None:
    manifest = _load("manifest.json")
    assert manifest["counts"] == {
        "companies": 3,
        "vacancies": 14,
        "candidates": 30,
        "projects": 32,
        "company_docs": 3,
    }
    assert len(_load("companies.json")) == 3
    assert len(_load("vacancies.json")) == 14
    assert len(_load("candidates.json")) == 30
    assert len(_load("projects.json")) == 32


def test_synthetic_dataset_v2_references() -> None:
    companies = {c["company_id"] for c in _load("companies.json")}
    candidates = {c["candidate_id"] for c in _load("candidates.json")}
    projects = {p["project_id"]: p for p in _load("projects.json")}
    for vacancy in _load("vacancies.json"):
        assert vacancy["company_id"] in companies
    for project in projects.values():
        assert project["candidate_id"] in candidates
    for candidate in _load("candidates.json"):
        assert candidate["project_ids"]
        for project_id in candidate["project_ids"]:
            assert project_id in projects
            assert projects[project_id]["candidate_id"] == candidate["candidate_id"]


def test_synthetic_dataset_v2_canonical_skills_and_hard_cases() -> None:
    taxonomy_ids = {s.canonical_id for s in load_taxonomy()}
    candidates = _load("candidates.json")
    vacancies = _load("vacancies.json")

    for candidate in candidates:
        for skill in candidate["skills"]:
            assert skill["canonical_id"] in taxonomy_ids
            assert skill["observed_raw_term"]
            assert skill["taxonomy_version"] == "skills_v1"

    for vacancy in vacancies:
        for skill in vacancy["essential_skills"] + vacancy["desirable_skills"]:
            assert skill in taxonomy_ids

    # hard cases: alias, false friend, empty evidence
    alias = next(c for c in candidates if c["candidate_id"] == "can-029")
    assert {s["observed_raw_term"] for s in alias["skills"]} >= {"JS", "Postgres", "Node"}
    false_friend = next(c for c in candidates if c["candidate_id"] == "can-030")
    canon = {s["canonical_id"] for s in false_friend["skills"]}
    assert {"java", "javascript"}.issubset(canon)
    projects = {p["project_id"]: p for p in _load("projects.json")}
    assert projects["prj-032"]["stack"] == []
    assert projects["prj-032"]["source_url"] is None


def test_synthetic_dataset_v2_has_company_docs() -> None:
    base = _repo_root() / "data" / "synthetic" / "v2" / "company_docs"
    docs = list(base.glob("*.json"))
    assert len(docs) == 3
    for doc_path in docs:
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        assert doc["company_id"]
        assert doc["content"]
        assert doc["source"] == "synthetic"


def test_synthetic_dataset_v2_date_coherence() -> None:
    reference = date(2026, 11, 26)
    for project in _load("projects.json"):
        start = date.fromisoformat(project["start_date"])
        end = date.fromisoformat(project["end_date"])
        assert start <= end, project["project_id"]
        assert abs((reference - start).days) <= 365
        assert abs((reference - end).days) <= 365
