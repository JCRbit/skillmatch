import json
from datetime import date
from pathlib import Path

from skillmatch.modules.skills import load_taxonomy


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load(name: str) -> object:
    path = _repo_root() / "data" / "synthetic" / "v1" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_synthetic_dataset_counts() -> None:
    manifest = _load("manifest.json")
    companies = _load("companies.json")
    vacancies = _load("vacancies.json")
    candidates = _load("candidates.json")
    projects = _load("projects.json")

    assert manifest["counts"] == {
        "companies": 3,
        "vacancies": 8,
        "candidates": 15,
        "projects": 16,
    }
    assert len(companies) == 3
    assert len(vacancies) == 8
    assert len(candidates) == 15
    assert len(projects) == 16


def test_synthetic_dataset_references() -> None:
    companies = {c["company_id"] for c in _load("companies.json")}
    candidates = {c["candidate_id"] for c in _load("candidates.json")}
    projects = {p["project_id"]: p for p in _load("projects.json")}
    vacancies = _load("vacancies.json")
    candidate_rows = _load("candidates.json")

    for vacancy in vacancies:
        assert vacancy["company_id"] in companies

    for project in projects.values():
        assert project["candidate_id"] in candidates

    for candidate in candidate_rows:
        assert candidate["project_ids"]
        for project_id in candidate["project_ids"]:
            assert project_id in projects
            assert projects[project_id]["candidate_id"] == candidate["candidate_id"]


def test_synthetic_dataset_uses_canonical_skills() -> None:
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


def test_synthetic_dataset_date_coherence() -> None:
    reference = date(2026, 11, 26)
    projects = _load("projects.json")
    for project in projects:
        start = date.fromisoformat(project["start_date"])
        end = date.fromisoformat(project["end_date"])
        assert start <= end, project["project_id"]
        assert abs((reference - start).days) <= 365, project["project_id"]
        assert abs((reference - end).days) <= 365, project["project_id"]

    for name in ["companies.json", "vacancies.json", "candidates.json", "projects.json"]:
        rows = _load(name)
        for row in rows:
            for key, value in row.items():
                if (
                    isinstance(value, str)
                    and len(value) >= 10
                    and value[4:5] == "-"
                    and value[7:8] == "-"
                ):
                    try:
                        parsed = date.fromisoformat(value[:10])
                    except ValueError:
                        continue
                    row_id = (
                        row.get("project_id")
                        or row.get("candidate_id")
                        or row.get("vacancy_id")
                        or row.get("company_id")
                    )
                    assert abs((reference - parsed).days) <= 365, f"{name}:{row_id}:{key}"
