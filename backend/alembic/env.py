"""Alembic environment configuration for database migrations."""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context

# --- CAMBIO 1: Importar nuestra Base y la URL ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from skillmatch.core.database import DATABASE_URL, Base
from skillmatch.modules.candidates.models import (  # noqa: F401
    CandidateProfile,
    CandidateProject,
    CandidateProjectEvidence,
    CandidateProjectEvidenceAudit,
    CandidateSkill,
)
from skillmatch.modules.companies.models import Company  # noqa: F401
from skillmatch.modules.identity.models import User  # noqa: F401
from skillmatch.modules.jobs.models import Vacancy  # noqa: F401

# ------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- CAMBIO 2: Conectar Alembic con nuestros modelos ---
target_metadata = Base.metadata
# -------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Convertimos cualquier URL asíncrona a síncrona para Alembic
    sync_url = DATABASE_URL
    if "postgresql+asyncpg://" in sync_url:
        sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    elif "sqlite+aiosqlite://" in sync_url:
        sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")

    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # --- CAMBIO 3: Forzar un motor síncrono para Alembic ---
    sync_url = DATABASE_URL
    if "postgresql+asyncpg://" in sync_url:
        sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    elif "sqlite+aiosqlite://" in sync_url:
        sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")

    connectable = create_engine(sync_url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
