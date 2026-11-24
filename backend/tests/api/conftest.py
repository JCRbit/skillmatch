"""Fixtures for the registration and login tests.

Every test gets an empty in-memory database, an application wired to it and a cheap password
hasher (production cost parameters would make the suite needlessly slow). Accounts are created
through the public API; :class:`UserStore` only inspects the database and prepares what the API
deliberately cannot create, such as administrators or suspended accounts.
"""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from skillmatch.api.auth import get_password_hasher
from skillmatch.api.deps import get_db_session, require_roles
from skillmatch.app import create_app
from skillmatch.core.config import Environment, Settings
from skillmatch.core.database import Base
from skillmatch.modules.identity.models import ACTIVE_ACCOUNT_STATUS, User, UserRole
from skillmatch.modules.identity.passwords import PasswordHasher

ACCOUNT_SECRET = "account-flow-test-secret-0123456789abcdef"  # noqa: S105 - synthetic value
TOKEN_TTL_SECONDS = 600

FAST_HASHER = PasswordHasher(log_n=4)
"""Cheapest scrypt cost. For tests only: production uses the defaults."""


class UserStore:
    """Synchronous helpers to inspect and prepare accounts in the test database."""

    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None:
        """Wrap the session factory of the test database."""
        self._factory = factory

    def get(self, email: str) -> User | None:
        """Return the stored account with this email, if any."""

        async def _get() -> User | None:
            async with self._factory() as session:
                result = await session.execute(select(User).where(User.email == email))
                return result.scalar_one_or_none()

        return asyncio.run(_get())

    def add(
        self,
        *,
        email: str,
        role: UserRole,
        password_hash: str | None,
        status: str = ACTIVE_ACCOUNT_STATUS,
    ) -> None:
        """Insert an account directly, bypassing the public registration rules."""

        async def _add() -> None:
            async with self._factory() as session:
                session.add(
                    User(email=email, role=role, status=status, password_hash=password_hash)
                )
                await session.commit()

        asyncio.run(_add())

    def set_status(self, email: str, status: str) -> None:
        """Change the status of an existing account."""

        async def _set() -> None:
            async with self._factory() as session:
                result = await session.execute(select(User).where(User.email == email))
                result.scalar_one().status = status
                await session.commit()

        asyncio.run(_set())


@pytest.fixture
def account_settings() -> Settings:
    """Settings with a signing secret and a known token lifetime."""
    return Settings(
        environment=Environment.TEST,
        auth_service_secret=SecretStr(ACCOUNT_SECRET),
        auth_token_ttl_seconds=TOKEN_TTL_SECONDS,
    )


@pytest.fixture
def account_db() -> Iterator[async_sessionmaker[AsyncSession]]:
    """An empty in-memory database with the schema created."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async def _create_schema() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(_create_schema())
    yield async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(engine.dispose())


@pytest.fixture
def user_store(account_db: async_sessionmaker[AsyncSession]) -> UserStore:
    """Inspection and preparation helpers for the test database."""
    return UserStore(account_db)


@pytest.fixture
def make_account_app(
    account_db: async_sessionmaker[AsyncSession],
) -> Callable[..., FastAPI]:
    """Return a function that builds an application wired to the test database."""

    def _make(settings: Settings, hasher: PasswordHasher = FAST_HASHER) -> FastAPI:
        app = create_app(settings)

        async def _session() -> AsyncIterator[AsyncSession]:
            async with account_db() as session:
                yield session

        app.dependency_overrides[get_db_session] = _session
        app.dependency_overrides[get_password_hasher] = lambda: hasher

        @app.get("/_probe/company-only")
        async def company_only(
            user: Annotated[User, Depends(require_roles(UserRole.EMPRESA))],
        ) -> dict[str, int]:
            return {"id": user.id}

        @app.get("/_probe/admin-only")
        async def admin_only(
            user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
        ) -> dict[str, int]:
            return {"id": user.id}

        return app

    return _make


@pytest.fixture
def account_client(
    make_account_app: Callable[..., FastAPI], account_settings: Settings
) -> Iterator[TestClient]:
    """Client of an application that is able to issue tokens."""
    with TestClient(make_account_app(account_settings), raise_server_exceptions=False) as client:
        yield client
