# Continuous integration

The pipeline lives in `.github/workflows/ci.yml` and runs on every pull request, on pushes to
`main` and on demand (`workflow_dispatch`). A pull request can only be merged when the single
required check **`CI · gate`** is green; that check succeeds only if every job below succeeded.

## Jobs

| Job (check name) | What it verifies | Run it locally |
|---|---|---|
| `Docs · enlaces internos` | Internal Markdown links resolve | — |
| `Security · escaneo heurístico de secretos` | Fast regex scan for well-known secret formats | — |
| `Security · gitleaks` | Full Git history scanned for secrets | `gitleaks detect --source .` |
| `Code · lint y tests` | Backend: ruff, format, mypy (strict), pytest + coverage ≥ 85 %. Frontend: lint, type check, unit tests, build | see below |
| `Audit · dependency vulnerabilities` | Known CVEs in locked **runtime** dependencies (`pip-audit`, `npm audit --audit-level=high`) | see below |
| `Database · migrations on a temporary database` | `alembic upgrade head`, `downgrade base`, `upgrade head` and `alembic check` on a throwaway PostgreSQL | see below |
| `Infra · compose config and image build` | `docker compose config` is valid and the API development image builds | `docker compose config -q && docker compose build api` |
| `CI · gate` | Aggregates all of the above; the only check that needs to be required | — |

Jobs whose code does not exist yet (frontend, Alembic, compose) print a `notice` annotation and skip
their steps, so a skipped step is always visible in the run summary instead of passing silently.

### Local equivalents

```bash
# Backend (from backend/)
uv sync --locked
uv run ruff check . && uv run ruff format --check . && uv run mypy
uv run pytest --cov --cov-report=term-missing

# Dependency audit (from backend/)
uv export --locked --no-dev --no-emit-project --format requirements-txt -o /tmp/requirements.txt
uvx pip-audit --strict --no-deps --disable-pip --requirement /tmp/requirements.txt

# Frontend (from frontend/)
npm ci && npm run lint && npm run typecheck --if-present && npm test && npm run build
npm audit --omit=dev --audit-level=high

# Migrations (from backend/, with the stack running: docker compose up -d db)
export SKILLMATCH_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/DB
uv run alembic upgrade head && uv run alembic downgrade base && uv run alembic upgrade head
uv run alembic check
```

## Contracts with other tasks

| Task | What the pipeline expects |
|---|---|
| P-02 (frontend) | `frontend/package-lock.json` committed; npm scripts `lint`, `test` (single run, no watch mode) and `build`; compatible with Node 22 (`NODE_VERSION` in `ci.yml`). A separate `typecheck` script is optional: type checking already runs inside `npm run build` (`tsc -b && vite build`) |
| B-01 (data model) | `backend/alembic.ini`; Alembic's `env.py` reads the database URL from `SKILLMATCH_DATABASE_URL` and exposes `target_metadata` so `alembic check` can detect drift |
| P-03 (compose) | `compose.yaml` and `.env.example` at the repository root; `.env.example` must contain placeholders only |

## Required checks and branch protection

Require only `CI · gate` (plus any check you already require, such as `Code · lint y tests`).
Job names are the check names, so renaming a job requires updating the protection rule.

Classic branch protection (needs admin rights). Replace `OWNER/REPO`:

```powershell
@'
{ "strict": true, "contexts": ["CI · gate", "Code · lint y tests"] }
'@ | Set-Content -Encoding utf8 required-checks.json

gh api --method PATCH repos/OWNER/REPO/branches/main/protection/required_status_checks --input required-checks.json
gh api repos/OWNER/REPO/branches/main/protection/required_status_checks
```

If the repository uses a **ruleset** instead (the endpoint above returns 404), edit it under
*Settings → Rules → Rulesets → Require status checks to pass* and add `CI · gate`.

`strict: true` forces branches to be up to date with `main` before merging. Set it to `false` if the
rebase overhead outweighs the benefit for the team.

### Verify that a red pull request cannot be merged

1. Create a branch, break one test on purpose and open a regular (non-draft) pull request.
   A draft cannot be merged regardless of its checks, so it would not prove anything.
2. Wait for the run: `CI · gate` must be red and the pull request's merge state must be
   `BLOCKED` (`gh pr view --json mergeStateStatus`). Do not try to merge it.
3. Close the pull request and delete the branch.

If the protection rule does not apply to administrators, an admin can still bypass it. Enable
*Do not allow bypassing the above settings* (classic: *Include administrators*) so the rule holds
for everyone.

## Secret scanning

- `Security · gitleaks` is free for personal accounts. Organisation accounts need a
  `GITLEAKS_LICENSE` repository secret.
- If it reports a harmless placeholder, add a targeted allowlist in `.gitleaks.toml` (one rule or
  path) instead of disabling the job. If the finding is a real credential, **rotate it first**; removing
  it from the latest commit does not remove it from history.

## Dependency updates

`.github/dependabot.yml` opens one grouped pull request per ecosystem every Monday, with
Conventional Commit prefixes (`uv`, `npm`, Docker, Docker Compose and GitHub Actions). GitHub raises
security updates separately and immediately.

## Known limitations

- Actions are pinned to major tags (`@v4`, `@v5`, `@v2`), not to commit SHAs. Pinning to SHAs is
  the stricter option; Dependabot can keep SHA pins up to date.
- `uvx pip-audit` installs the latest `pip-audit` on every run. Pin it (`uvx pip-audit==X.Y.Z`) if
  the tool itself must be reproducible.
- Only runtime dependencies are audited. Development tooling is covered by Dependabot alerts.
- The frontend checks were verified on Node 22 in a clean container (`node:22-alpine`), the version used by CI and by the `web` service in `compose.yaml`.
- The migration job needs `psycopg` and Alembic as project dependencies (task B-01).
- Playwright end-to-end tests (task Q-01) will be added as a separate job and included in `gate`.

## Changing the pipeline

1. Keep every new job under `needs:` of `gate`, otherwise it will not block merging.
2. Give every job a `timeout-minutes`.
3. Keep `permissions` minimal; widen them per job, never globally.
4. Document the job and its local equivalent in this file.
