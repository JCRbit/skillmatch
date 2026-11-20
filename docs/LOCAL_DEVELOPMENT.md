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

## Commands

These commands match `compose.yaml`, `backend/` and `frontend/`.

### Prerequisites

- Docker Desktop (or Docker Engine) with **Compose v2**: use `docker compose`, not `docker-compose`.
- [uv](https://docs.astral.sh/uv/) only if you also run the backend outside Docker (see `backend/README.md`).

### Run the stack

```bash
cp .env.example .env          # PowerShell: Copy-Item .env.example .env
# edit .env: replace the local-only passwords (URL-safe characters only)
docker compose up --build
```

First start builds the API image and initialises the database; later starts take seconds.

| Service | URL / port | Notes |
|---|---|---|
| API | <http://localhost:8000> | `GET /health`, interactive docs at `/docs` |
| Database | `localhost:5432` | PostgreSQL 16, data in the `postgres_data` volume |
| Web | <http://localhost:5173> | Vite dev server with hot reload (`frontend/`) |

All ports are bound to `127.0.0.1` and can be changed with `API_PORT`, `DB_PORT` and `WEB_PORT`.

### Verify a clean start

```bash
docker compose down -v        # remove containers and the database volume
docker compose up --build -d
docker compose ps             # db and api must report "healthy"; web must be "Up"
curl http://localhost:8000/health        # PowerShell: Invoke-RestMethod http://localhost:8000/health
# expected: {"status":"ok"}
curl -I http://localhost:5173            # PowerShell: (Invoke-WebRequest -UseBasicParsing http://localhost:5173).StatusCode
# expected: HTTP 200 (Vite dev server; the first start runs `npm ci`, give it a few seconds)
```

### Everyday commands

| Goal | Command |
|---|---|
| Follow API logs | `docker compose logs -f api` |
| Follow frontend logs | `docker compose logs -f web` |
| Run the backend tests in the container | `docker compose exec api pytest` |
| Lint / type-check in the container | `docker compose exec api ruff check .` and `docker compose exec api mypy` |
| Frontend tests / lint in the container | `docker compose exec web npm test` and `docker compose exec web npm run lint` |
| Reinstall frontend dependencies | `docker compose restart web` (the service runs `npm ci` on every start) |
| Open a SQL shell | `docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'` |
| Rebuild after changing dependencies | `docker compose up --build` (after `uv add ...` and committing `uv.lock`) |
| Stop, keep data | `docker compose down` |
| Stop and **delete the database** | `docker compose down -v` |

Source code under `backend/src`, `backend/tests` and `frontend/` is bind-mounted, so edits on the host
reload the API and the Vite dev server automatically. Changing `backend/pyproject.toml` or
`backend/uv.lock` requires a rebuild (`docker compose up --build`); changing `frontend/package.json`
or `frontend/package-lock.json` requires `docker compose restart web`.

### Frontend without Docker

The `web` service already runs the Vite dev server. To work on the frontend directly (Node 22):

```bash
cd frontend
npm ci              # install exactly what package-lock.json says
npm run dev         # Vite dev server with hot reload
npm run lint        # ESLint
npm test            # unit tests (Vitest, single run)
npm run build       # type check (tsc -b) and production build
```

### Troubleshooting

- **`Set POSTGRES_PASSWORD in .env`**: you have not created `.env` yet; copy `.env.example`.
- **Changed `POSTGRES_PASSWORD` but the API cannot connect**: PostgreSQL only reads the credentials
  when it initialises an empty volume. Run `docker compose down -v` (this deletes local data).
- **Port already in use**: change `API_PORT`, `DB_PORT` or `WEB_PORT` in `.env`.
- **Code changes are not reloaded on Windows/macOS**: the stack already enables polling
  (`WATCHFILES_FORCE_POLLING`, `CHOKIDAR_USEPOLLING`); check that the files are inside the
  shared drives/folders configured in Docker Desktop.
- **Frontend dependency problems in the `web` container**: its `node_modules` live in the
  `web_node_modules` volume, not in your working copy. To recreate them without touching the
  database: `docker compose rm -sf web`, then `docker volume rm skillmatch_web_node_modules`, then
  `docker compose up -d web`.
- **Reproducible builds**: set `UV_VERSION` in `.env` to the output of `uv --version`.

Use only synthetic data in these containers. The development credentials in `.env.example` must never
be reused outside a local machine.
