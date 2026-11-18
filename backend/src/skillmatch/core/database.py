import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# URL de conexión a PostgreSQL.
# Se puede sobreescribir con la variable de entorno SKILLMATCH_DATABASE_URL
# (el prefijo SKILLMATCH_ es el que usa el proyecto). Si no está definida,
# usamos una base de datos local por defecto.
DATABASE_URL = os.getenv(
    "SKILLMATCH_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/skillmatch",
)

# Motor asíncrono: gestiona las conexiones reales con la base de datos.
engine = create_async_engine(DATABASE_URL, echo=False)

# Fábrica de sesiones: cada operación con la BD pedirá una sesión aquí.
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Clase Base: TODAS las tablas heredarán de ella.
# Alembic la usa para descubrir qué tablas tiene que crear.
class Base(DeclarativeBase):
    pass