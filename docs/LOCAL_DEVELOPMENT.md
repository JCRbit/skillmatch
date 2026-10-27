# Local development / first bootstrap

## Before any code runs

- Complete phase-0 audit. Do not run `docker compose up`, tests or notebooks inside legacy without source inspection and approval.
- Install approved versions of Git, Docker/Compose, Python, Node and chosen harness. Pin versions in team setup notes after compatibility test.
- Create local `.env` from `.env.example`, replace local-only passwords, ensure `.env` is ignored.
- Use synthetic test profiles/offers. No real CVs or tokens.

## Suggested phases

1. Docs-only commit containing this foundation pack.
2. Add approved Compose services and migration skeleton as separate reviewed PR.
3. Add backend package and health endpoints; CI lint/type/unit tests.
4. Add database models/migrations and role/tenant tests.
5. Add frontend package with mock fixtures.
6. Add Qdrant/embeddings once matching data contract is agreed.
7. Add Redis/worker only for durable background tasks.

## Commands to define after implementation exists

Record exact commands in this file once `pyproject.toml`, frontend package scripts and compose config exist. Do not copy commands from another repo without checking they match the repository.
