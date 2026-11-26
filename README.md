# SkillMatch (codename provisional / provisional codename)

Plataforma de matching profesional bidireccional para perfiles junior, basada en competencias demostrables, explicabilidad, privacidad y supervisión humana.  
Bidirectional professional matching platform for junior profiles, based on demonstrable competencies, explainability, privacy, and human oversight.

> **Estado / Status**: MVP en desarrollo activo. El codename `SkillMatch` es provisional. / MVP in active development. The `SkillMatch` codename is provisional.

## Qué es / What it is

**ES:** SkillMatch conecta talento junior y empresas a partir de evidencias de competencias (perfil, skills declaradas, proyectos, vacantes), con matching explicable, control de visibilidad/consentimiento y enfoque privacy-by-design.  
**EN:** SkillMatch connects junior talent and companies through competency evidence (profile, declared skills, projects, vacancies), with explainable matching, visibility/consent controls, and a privacy-by-design approach.

## Estado real / Current status

**ES (resumen `main`):**
- **Backend** (FastAPI, Python 3.12, SQLAlchemy async, Alembic): app factory, config por entorno, health/readiness/version, auth/register/login, roles/autorización base, perfil de candidato y skills declaradas (B-03), taxonomía de skills S-01.
- **Frontend** (React + TypeScript + Vite): shell, flujo auth y rutas protegidas base.
- **Infra local**: `compose.yaml` con PostgreSQL, API y web.
- **Calidad**: tests backend, lint/format/mypy, CI en GitHub Actions.

**EN (`main` summary):**
- **Backend** (FastAPI, Python 3.12, SQLAlchemy async, Alembic): app factory, env config, health/readiness/version, auth/register/login, base roles/authorization, candidate profile and declared skills (B-03), skills taxonomy S-01.
- **Frontend** (React + TypeScript + Vite): shell, auth flow, and base protected routes.
- **Local infra**: `compose.yaml` with PostgreSQL, API, and web.
- **Quality**: backend tests, lint/format/mypy, GitHub Actions CI.

**Pendiente / Pending (PRs, not merged):** S-04 synthetic dataset (#125), S-05 seed CLI (#127), and other backlog items.

## Quickstart (local)

### Requisitos / Requirements

- Docker + Docker Compose
- Git
- (Opcional / Optional, backend local dev) [uv](https://docs.astral.sh/uv/)
- (Opcional / Optional, frontend local dev) Node.js 24+ / npm

### 1) Clonar y configurar / Clone and configure

```bash
git clone https://github.com/JCRbit/skillmatch.git
cd skillmatch
cp .env.example .env
```

Edita `.env` / Edit `.env`:

- `POSTGRES_PASSWORD`: contraseña local de desarrollo / local dev password.
- `SKILLMATCH_AUTH_SERVICE_SECRET`: secreto para firmar tokens / token signing secret.  
  Generar / Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

### 2) Levantar con Docker Compose / Start with Docker Compose

```bash
docker compose up --build
```

Servicios / Services:

- API: http://127.0.0.1:8000
- Docs API (non-prod): http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Readiness: http://127.0.0.1:8000/ready
- Version: http://127.0.0.1:8000/version
- Frontend (Vite dev): http://127.0.0.1:5173

> `compose.yaml` es solo para desarrollo local; puertos en `127.0.0.1`. / Local dev only; ports bound to `127.0.0.1`.

### 3) Tests (backend)

```bash
cd backend
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest -q
```

### 4) Seed / datos sintéticos / synthetic data

- **S-04 dataset**: `data/synthetic/v1/` (cuando se mergee PR #125 / when PR #125 is merged, or on that branch).
- **S-05 seed CLI**: `python -m skillmatch.cli.seed --dry-run` (cuando se mergee PR #127 / when PR #127 is merged, or on that branch).

**ES:** Mientras no estén en `main`, usa la API/UI y fixtures de tests. No uses datos reales.  
**EN:** Until merged into `main`, use the API/UI and test fixtures. Do not use real data.

## Estructura del repositorio / Repository structure

```text
.
├── .github/                 # CI, templates, workflows
├── backend/                 # FastAPI + domain modules
│   ├── alembic/             # Migrations
│   ├── src/skillmatch/      # Source code
│   └── tests/               # unit/api/architecture
├── frontend/                # React + TypeScript + Vite
├── docs/                    # Requirements, architecture, ADRs, audits, runbooks
├── scripts/                 # Support scripts
├── compose.yaml             # Local dev stack
├── .env.example             # Environment template
├── AGENTS.md                # Agent/contribution rules
└── START_HERE.md            # Foundational context
```

## Desarrollo por componente / Component development

- Backend: [`backend/README.md`](backend/README.md)
- Frontend: [`frontend/README.md`](frontend/README.md)
- Local dev/compose: [`docs/LOCAL_DEVELOPMENT.md`](docs/LOCAL_DEVELOPMENT.md)
- Observability: [`docs/OBSERVABILITY_RUNBOOK.md`](docs/OBSERVABILITY_RUNBOOK.md)

## Documentación clave / Key docs

- [`docs/INDEX.md`](docs/INDEX.md) — índice maestro / master index
- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md)
- [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md)
- [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md)
- [`docs/SECURITY_PRIVACY.md`](docs/SECURITY_PRIVACY.md)

## Reglas importantes / Important rules

- **ES:** No usar datos reales, CVs reales, secretos ni tokens en Git, issues, PRs o logs.
- **EN:** Do not use real data, real CVs, secrets, or tokens in Git, issues, PRs, or logs.
- **ES:** El legacy `TinderJob_Fork` se audita en modo read-only hasta aprobación explícita de PO (ver `AGENTS.md`).
- **EN:** The `TinderJob_Fork` legacy is audited in read-only mode until explicit PO approval (see `AGENTS.md`).
- **ES:** El matching/afinidad no es decisión automática de contratación; requiere explicabilidad y supervisión humana.
- **EN:** Matching/affinity is not an automatic hiring decision; it requires explainability and human oversight.

## Seguridad / Security

- Reporte de vulnerabilidades / Vulnerability reporting: [`SECURITY.md`](SECURITY.md)