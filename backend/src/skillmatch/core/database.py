"""Database configuration and SQLAlchemy setup for async PostgreSQL connections."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from skillmatch.core.config import get_settings

# Obtener la configuración centralizada (lee .env o variables de entorno con prefijo SKILLMATCH_)
settings = get_settings()
DATABASE_URL = settings.database_url

# Motor asíncrono: gestiona las conexiones reales con la base de datos.
engine = create_async_engine(DATABASE_URL, echo=False)

# Fábrica de sesiones: cada operación con la BD pedirá una sesión aquí.
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Alembic uses Base.metadata to discover which tables need to
    be created or updated during migrations.
    """

    pass
