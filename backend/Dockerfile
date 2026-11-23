# syntax=docker/dockerfile:1
#
# Backend image.
#
# Stages
#   base         Python runtime, uv and an unprivileged user.
#   development  Dev dependencies and auto-reload; the stage used by compose.yaml (task P-03).
#
# A `production` stage (no dev dependencies, no reload) is added by task P-06.
#
# Build arguments
#   PYTHON_VERSION  Must match backend/.python-version.
#   UV_VERSION      uv release to copy into the image. Pin it to the output of `uv --version`
#                   (e.g. 0.9.5) for reproducible builds; `latest` is only a convenience default.

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
