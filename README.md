# SkillMatch (codename provisional)

Plataforma de matching profesional bidireccional para perfiles junior, basada en competencias demostrables, explicabilidad, privacidad y supervisión humana.

> **Estado**: MVP en desarrollo activo. El codename `SkillMatch` es provisional (decisión de nombre público pendiente de PO). Este README describe el estado real del repositorio en la rama `main`.

## Qué es

SkillMatch conecta talento junior y empresas a partir de evidencias de competencias (perfil, skills declaradas, proyectos, vacantes), con:

- matching explicable (no decisión automática opaca),
- control de visibilidad y consentimiento,
- separación de identidad y perfil de talento,
- enfoque privacy-by-design y datos sintéticos en desarrollo/demo.

## Estado real

Implementado actualmente en `main` (resumen de alto nivel):

- **Backend** (FastAPI, Python 3.12, SQLAlchemy async, Alembic): app factory, configuración por entorno, health/readiness/version, auth/register/login, roles y autorización base, perfil de candidato y skills declaradas (B-03), taxonomía de skills S-01.
- **Frontend** (React + TypeScript + Vite): shell frontend, flujo auth y rutas protegidas base.
- **Infra local**: `compose.yaml` con PostgreSQL, API y web.
- **Calidad**: tests backend, lint/format/mypy, CI en GitHub Actions.

Pendiente o en PR (no asumir como mergeado): dataset sintético S-04 (#125), seed CLI S-05 (#127), y otras funcionalidades del backlog.

## Quickstart (local)

### Requisitos

- Docker + Docker Compose
- Git
- (Opcional para desarrollo backend local) [uv](https://docs.astral.sh/uv/)
- (Opcional para desarrollo frontend local) Node.js 24+ / npm

### 1) Clonar y configurar entorno

```bash
git clone https://github.com/JCRbit/skillmatch.git
cd skillmatch
cp .env.example .env
```

Edita `.env` y reemplaza valores locales. Como mínimo:

- `POSTGRES_PASSWORD`: contraseña local (solo desarrollo).
- `SKILLMATCH_AUTH_SERVICE_SECRET`: secreto para firmar tokens (puedes generar uno con `python -c "import secrets; print(secrets.token_urlsafe(48))"`). Sin él, el login puede responder 503.

### 2) Levantar con Docker Compose

```bash
docker compose up --build
```

Servicios:

- API: http://127.0.0.1:8000
- Docs API (entornos no producción): http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Readiness: http://127.0.0.1:8000/ready
- Version: http://127.0.0.1:8000/version
- Frontend (Vite dev): http://127.0.0.1:5173

> `compose.yaml` es solo para desarrollo local. Los puertos se publican en `127.0.0.1`.

### 3) Tests (backend)

En otra terminal:

```bash
cd backend
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest -q
```

### 4) Seed / datos sintéticos

- Dataset sintético versionado (S-04): `data/synthetic/v1/` (disponible cuando el PR #125 esté mergeado o en la rama correspondiente).
- Cargador idempotente CLI (S-05): `python -m skillmatch.cli.seed --dry-run` (disponible cuando el PR #127 esté mergeado o en la rama correspondiente).

Mientras S-04/S-05 no estén en `main`, usa la API/UI y fixtures de tests para desarrollo local. No uses datos reales.

## Estructura del repositorio

```text
.
├── .github/                 # CI, plantillas y workflows
├── backend/                 # API FastAPI + módulos de dominio
│   ├── alembic/             # Migraciones
│   ├── src/skillmatch/      # Código fuente
│   └── tests/               # unit/api/architecture
├── frontend/                # React + TypeScript + Vite
├── docs/                    # Requisitos, arquitectura, ADRs, auditoría, runbooks
├── scripts/                 # Scripts de soporte (smoke, legacy inventory, checks)
├── compose.yaml             # Stack local de desarrollo
├── .env.example             # Plantilla de variables de entorno
├── AGENTS.md                # Reglas para agentes/contribución asistida
└── START_HERE.md            # Contexto fundacional / fase 0
```

## Desarrollo por componente

- Backend: ver [`backend/README.md`](backend/README.md)
- Frontend: ver [`frontend/README.md`](frontend/README.md)
- Desarrollo local/compose: ver [`docs/LOCAL_DEVELOPMENT.md`](docs/LOCAL_DEVELOPMENT.md)
- Observabilidad: ver [`docs/OBSERVABILITY_RUNBOOK.md`](docs/OBSERVABILITY_RUNBOOK.md)

## Documentación clave

- [`docs/INDEX.md`](docs/INDEX.md) — índice maestro
- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) — alcance y principios
- [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) — requisitos y criterios
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — arquitectura objetivo
- [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md) — decisiones
- [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) — modelo de datos lógico
- [`docs/SECURITY_PRIVACY.md`](docs/SECURITY_PRIVACY.md) — seguridad y privacidad

## Reglas importantes

- No usar datos reales, CVs reales, secretos ni tokens en Git, issues, PRs o logs.
- El legacy `TinderJob_Fork` se audita en modo read-only hasta aprobación explícita de PO (ver `AGENTS.md`).
- El matching/afinidad no es decisión automática de contratación; requiere explicabilidad y supervisión humana.

## Licencia y seguridad

- Licencia: ver [`LICENSE`](LICENSE) si está presente en la rama actual.
- Reporte de vulnerabilidades: ver [`SECURITY.md`](SECURITY.md).