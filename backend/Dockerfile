# syntax=docker/dockerfile:1
#
# Backend image.
#
# Stages
#   base         Python runtime, uv and an unprivileged user.
#   development  Dev dependencies and auto-reload; the stage used by compose.yaml (task P-03).
#   builder      Resolves the locked runtime dependencies and installs the project (no dev tools).
#   production   Minimal runtime image published to Docker Hub (task P-06): no uv, no dev
#                dependencies, no tests, no reload, unprivileged user, built-in health check.
#
# Build arguments
#   PYTHON_VERSION  Must match backend/.python-version.
#   UV_VERSION      uv release to copy into the image. Pin it to the output of `uv --version`
#                   (e.g. 0.9.5) for reproducible builds; `latest` is only a convenience default.
#   GIT_SHA         (production) Commit the image is built from. Recorded in the
#                   `org.opencontainers.image.revision` label and in SKILLMATCH_GIT_SHA.
#   BUILD_DATE      (production) RFC 3339 build timestamp, recorded in the `created` label.
#   SOURCE_URL      (production) Repository URL, recorded in the `source` label.
#
# Build and smoke-test the production image locally (needs Docker only):
#   docker build --target production --build-arg GIT_SHA="$(git rev-parse HEAD)" \
#     --tag skillmatch-api:local backend
#   bash scripts/smoke_test_image.sh skillmatch-api:local "$(git rev-parse HEAD)"

ARG PYTHON_VERSION=3.12
ARG UV_VERSION=latest

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/home/app/.cache/uv \
    PATH="/opt/venv/bin:${PATH}"

COPY --from=uv /uv /uvx /bin/

# Run as an unprivileged user with a fixed UID/GID.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app \
    && mkdir /app /opt/venv \
    && chown app:app /app /opt/venv

WORKDIR /app
USER app

FROM base AS development

# 1) Dependencies only: this layer is rebuilt only when pyproject.toml or uv.lock change.
COPY --chown=app:app pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/home/app/.cache/uv,uid=10001,gid=10001 \
    uv sync --locked --no-install-project

# 2) Project sources, installed in editable mode so bind-mounted code is picked up.
COPY --chown=app:app README.md ./
COPY --chown=app:app alembic.ini ./alembic.ini
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app src ./src
COPY --chown=app:app tests ./tests
RUN --mount=type=cache,target=/home/app/.cache/uv,uid=10001,gid=10001 \
    uv sync --locked

EXPOSE 8000

# 0.0.0.0 is intentional: the container port is published to 127.0.0.1 only by compose.yaml.
CMD ["uvicorn", "skillmatch.app:create_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "src"]

# --------------------------------------------------------------------------- #
# Production
# --------------------------------------------------------------------------- #
FROM base AS builder

# 1) Locked runtime dependencies only (`--no-dev`): rebuilt only when pyproject.toml or uv.lock
#    change. `--locked` fails if uv.lock is stale, so the image never resolves new versions.
COPY --chown=app:app pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/home/app/.cache/uv,uid=10001,gid=10001 \
    uv sync --locked --no-dev --no-install-project

# 2) The project itself, installed as a regular (non-editable) package inside the virtualenv, so
#    the final image does not need the sources, uv or a build toolchain.
COPY --chown=app:app README.md ./
COPY --chown=app:app src ./src
RUN --mount=type=cache,target=/home/app/.cache/uv,uid=10001,gid=10001 \
    uv sync --locked --no-dev --no-editable

FROM python:${PYTHON_VERSION}-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:${PATH}" \
    SKILLMATCH_ENVIRONMENT=production

# Same fixed UID/GID as the development image. No home directory and no login shell are needed.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app \
    && mkdir /app \
    && chown app:app /app

# The virtualenv and the migrations are owned by root and read-only for the application user:
# the code that runs is exactly the code that was built.
COPY --from=builder --chown=root:root /opt/venv /opt/venv

WORKDIR /app
# Alembic is a runtime dependency, so migrations can run from this same image as a one-off
# command (`alembic upgrade head`) before the new version starts serving traffic.
COPY --chown=root:root alembic.ini ./
COPY --chown=root:root alembic ./alembic

# Build metadata comes last so that a new commit does not invalidate the layers above.
ARG GIT_SHA=unknown
ARG BUILD_DATE=unknown
ARG SOURCE_URL=
ENV SKILLMATCH_GIT_SHA=${GIT_SHA}
LABEL org.opencontainers.image.title="skillmatch-api" \
      org.opencontainers.image.description="SkillMatch backend API (FastAPI)" \
      org.opencontainers.image.source="${SOURCE_URL}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.created="${BUILD_DATE}"

USER app

EXPOSE 8000

# Liveness only (GET /health performs no dependency checks). The image has no curl, so use the
# interpreter that is already there.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

# SKILLMATCH_ENVIRONMENT=production disables the interactive API docs and makes the settings
# validation reject debug mode and wildcard CORS. Override it only for staging.
# 0.0.0.0 is intentional: the container port is published by the orchestrator, not by this file.
CMD ["uvicorn", "skillmatch.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
