# Synthetic Dataset v1 — SkillMatch

## Purpose
Synthetic, versioned seed data for MVP development, testing, and demos. This dataset is **not** real user data.

## Scope (Issue S-04)
- 3 companies
- 8 vacancies
- 15 candidate profiles
- 16 projects (all candidates have >=1 project; one candidate has 2 for variety)
- Versioned under `data/synthetic/v1`

## Files
- `manifest.json` — dataset metadata and counts.
- `companies.json` — 3 synthetic companies.
- `vacancies.json` — 8 synthetic vacancies with essential/desirable skills.
- `candidates.json` — 15 synthetic candidate profiles with skills and project refs.
- `projects.json` — synthetic projects used as evidence refs.
- `quality_report.json` — DAMA-inspired basic quality checks and score.

## Data rules
- **No real data**: names, emails, URLs, repos, and company details are fictitious. Emails use `example.com`; repos use `github.com/example-skillmatch/...`; demo URLs use `demo.example-skillmatch.dev`.
- **Taxonomy alignment**: candidate skills and vacancy skills use canonical IDs from `backend/src/skillmatch/modules/skills/data/skills_v1.csv` (taxonomy `skills_v1`).
- **Raw term preserved**: candidate skills include `observed_raw_term` to support normalization/evidence flows.
- **Traceability**: candidates reference project IDs; skills include `evidence_refs`.

## DAMA-inspired quality scoring (v1)
As agreed in team discussion (Jesús, 23/11), we track 3 dimensions with a 0-100 score and weights:

| Dimension | Weight | What it checks |
|---|---:|---|
| Completeness | 40% | Required fields present and non-empty |
| Uniqueness / Integrity | 35% | No duplicate IDs/emails |
| Timeliness / Actuality | 25% | Date fields within +/-365 days of reference date |

Total score is computed in `quality_report.json`. Target for seed release: >= 95.

## Known limitations
- This dataset is a logical seed, not a DB dump; S-05 will map/load it when target tables/models exist.
- Skills and roles are simplified for MVP; they do not represent real hiring criteria.
- Projects are manual portfolio evidence only; no external scraping or real GitHub ingestion.
- Salary ranges, locations, and availability are synthetic placeholders.

## Usage
- Use as fixture/seed source for development and tests.
- Do not treat as production or real-world statistical evidence.
- For S-05, load idempotently by stable IDs (`company_id`, `vacancy_id`, `candidate_id`, `project_id`).

## Change policy
- Any change to v1 files must update `manifest.json` and regenerate `quality_report.json`.
- Breaking schema changes should create `data/synthetic/v2/`.
