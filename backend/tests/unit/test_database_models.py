from sqlalchemy import Enum
from sqlalchemy.engine import make_url

from skillmatch.core.database import (
    DATABASE_URL,
    Base,
    async_session_maker,
    engine,
)
from skillmatch.modules.identity.models import User, UserRole


def test_database_engine_and_session_configuration() -> None:
    assert engine.url == make_url(DATABASE_URL)
    assert engine.url.drivername == "postgresql+asyncpg"
    assert async_session_maker.kw["expire_on_commit"] is False
    assert Base.metadata is not None


def test_user_role_values() -> None:
    assert UserRole.TALENTO.value == "talento"
    assert UserRole.EMPRESA.value == "empresa"
    assert UserRole.ADMIN.value == "admin"


def test_user_model_table_and_columns() -> None:
    assert User.__tablename__ == "users"

    columns = User.__table__.columns

    assert columns["id"].primary_key
    assert columns["email"].unique
    assert columns["email"].nullable is False

    assert columns["password_hash"].nullable is True
    assert columns["role"].nullable is False
    assert isinstance(columns["role"].type, Enum)
    assert columns["role"].type.enum_class is UserRole

    assert columns["status"].default.arg == "active"
    assert columns["created_at"].nullable is False
    created_at_type = columns["created_at"].type
    assert getattr(created_at_type, "timezone", False) is True
    assert columns["last_login_at"].nullable is True
