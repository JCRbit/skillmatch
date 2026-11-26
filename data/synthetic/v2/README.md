# Synthetic Dataset v2 ? SkillMatch

Extends v1 with +15 candidates, +6 vacancies, company RAG docs, and hard cases.

## Counts
- 3 companies
- 14 vacancies
- 30 candidates
- 32 projects
- 3 company docs (RAG)

## Hard cases
- **Alias**: can-029 uses JS/Postgres/Node as observed raw terms mapped to canonical skills.
- **False friend**: can-030 includes Java and JavaScript as distinct skills (Java/JavaScript confusion case).
- **Empty evidence**: prj-032 has no stack and no technical evidence; candidate has project with no technical signal.

## Company docs
`company_docs/` contains synthetic company documents for RAG ingestion experiments.

## Rules
- No real data. Synthetic emails/URLs only.
- Skills aligned to `skills_v1`.
- IDs stable; v2 is self-contained (includes v1 records).
