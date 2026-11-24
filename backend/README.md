# SkillMatch backend

Modular monolith built with **FastAPI**, **Pydantic 2** and **Python 3.12**.
Architecture rationale lives in [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (single package manager for this project; do not mix it with `pip`).

## First-time setup

```bash
cd backend
uv sync                 # creates .venv and installs the locked dependencies
uv run ruff format .    # normalise formatting once
uv run ruff check --fix .
```

## Daily commands

| Goal | Command |
|---|---|
| Run the API with auto-reload | `uv run uvicorn skillmatch.app:create_app --factory --reload` |
| Lint | `uv run ruff check .` |
| Check formatting | `uv run ruff format --check .` |
| Type-check (strict) | `uv run mypy` |
| Run tests | `uv run pytest` |
| Tests with coverage | `uv run pytest --cov --cov-report=term-missing` |
| Add a runtime dependency | `uv add <package>` (commit `pyproject.toml` **and** `uv.lock`) |
| Add a dev dependency | `uv add --dev <package>` |

The server listens on <http://127.0.0.1:8000>. Interactive docs are available at `/docs`
in every environment except `production`. A liveness probe is exposed at `GET /health`.

## Configuration

Settings are read from environment variables prefixed with `SKILLMATCH_` or from a local
`.env` file (never commit it). See `src/skillmatch/core/config.py` for the full list.

| Variable | Default | Notes |
|---|---|---|
| `SKILLMATCH_ENVIRONMENT` | `local` | `local`, `test`, `staging` or `production` |
| `SKILLMATCH_DEBUG` | `false` | Must stay `false` in `production` (enforced at start-up) |
| `SKILLMATCH_CORS_ALLOWED_ORIGINS` | `[]` | JSON list, e.g. `["http://localhost:5173"]`; `*` is rejected in `production` |
| `SKILLMATCH_AUTH_SERVICE_SECRET` | empty | Signs access tokens; at least 32 characters and **required** in `staging` and `production`. Empty: login answers 503 |
| `SKILLMATCH_AUTH_TOKEN_TTL_SECONDS` | `900` | Lifetime of an access token |

## Project layout

```text
src/skillmatch/
├── app.py            # create_app(): application factory (no import-time side effects)
├── core/             # cross-cutting concerns: settings, error model (no business logic)
├── api/              # HTTP layer: routers, dependencies, operational endpoints
└── modules/          # bounded contexts (identity, candidates, companies, jobs, ...)
tests/
├── unit/             # pure logic, no HTTP
├── api/              # HTTP behaviour through the ASGI app
└── architecture/     # import rules that keep the modular monolith modular
```

### Module boundaries (enforced by `tests/architecture`)

1. `core` never imports `api`, `modules` or `app`.
2. A module never imports `api` or `app`.
3. A module only imports another module through its package root
   (`from skillmatch.modules.jobs import ...`), never its internals
   (`skillmatch.modules.jobs.models`).
4. Imports are absolute; relative imports are banned by Ruff.

## Conventions

- Public functions, classes and modules carry Google-style docstrings in English.
- All code is fully typed; `mypy --strict` must pass.
- Errors raised by the application derive from `AppError` and are rendered as
  RFC 9457 *problem details* (`application/problem+json`). Validation errors never echo
  the offending input, to avoid leaking personal data.
- Configuration is injected (`SettingsDep`), never read from `os.environ` directly.
