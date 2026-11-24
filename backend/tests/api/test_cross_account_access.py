"""Tests for cross-account access control and the authentication boundary (FR-001, NFR-005).

The suite covers what the reviewer asked for:

- unauthenticated requests (no credential at all);
- invalid, forged, expired and unknown identities;
- inactive accounts;
- authenticated users with the three roles (``TALENTO``, ``EMPRESA``, ``ADMIN``);
- cross-account access answering 403 or 404 as appropriate, and administrator access.

Identities are no longer simulated with a client-supplied ``X-User-Id`` header: each request
carries a bearer token signed with the configured secret, and the user record is loaded from the
database, so these tests exercise the real authentication path.
"""

from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from skillmatch.api.deps import (
    CurrentUserDep,
    get_current_user,
    get_db_session,
    require_roles,
    verify_resource_ownership,
)
from skillmatch.app import create_app
from skillmatch.core.config import Settings
from skillmatch.core.database import Base
from skillmatch.core.security import create_service_token
from skillmatch.modules.identity.models import User, UserRole

TEST_SECRET = "test-secret-not-a-real-key"  # noqa: S105 - synthetic fixture value

TALENT_ID = 10
OTHER_TALENT_ID = 20
COMPANY_ID = 30
ADMIN_ID = 99
INACTIVE_ID = 40


@pytest.fixture
def settings() -> Settings:
    """Settings with a known signing secret, so tokens can be issued in the tests."""
    return Settings(
        environment="test",  # type: ignore[arg-type]
        auth_service_secret=TEST_SECRET,  # type: ignore[arg-type]
    )


@pytest.fixture
def session_factory() -> Iterator[async_sessionmaker[AsyncSession]]:
    """In-memory database holding one user per role, plus an inactive account."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = async_sessionmaker(engine, expire_on_commit=False)

    import asyncio

    async def _seed() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with factory() as session:
            session.add_all(
                [
                    User(
                        id=TALENT_ID,
                        email="talento@skillmatch.test",
                        role=UserRole.TALENTO,
                        status="active",
                        created_at=datetime.now(UTC),
                    ),
                    User(
                        id=OTHER_TALENT_ID,
                        email="otro-talento@skillmatch.test",
                        role=UserRole.TALENTO,
                        status="active",
                        created_at=datetime.now(UTC),
                    ),
                    User(
                        id=COMPANY_ID,
                        email="empresa@skillmatch.test",
                        role=UserRole.EMPRESA,
                        status="active",
                        created_at=datetime.now(UTC),
                    ),
                    User(
                        id=ADMIN_ID,
                        email="admin@skillmatch.test",
                        role=UserRole.ADMIN,
                        status="active",
                        created_at=datetime.now(UTC),
                    ),
                    User(
                        id=INACTIVE_ID,
                        email="inactivo@skillmatch.test",
                        role=UserRole.TALENTO,
                        status="suspended",
                        created_at=datetime.now(UTC),
                    ),
                ]
            )
            await session.commit()

    asyncio.run(_seed())
    yield factory
    asyncio.run(engine.dispose())


@pytest.fixture
def auth_app(
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
) -> FastAPI:
    """Application with probe routes that apply authentication and ownership checks."""
    app = create_app(settings)

    async def _override_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = _override_session

    @app.get("/_test/me")
    async def read_me(current_user: CurrentUserDep) -> dict[str, str | int]:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value,
        }

    @app.get("/_test/resources/{owner_id}")
    async def get_resource(
        owner_id: int,
        current_user: CurrentUserDep,
    ) -> dict[str, int]:
        verify_resource_ownership(
            resource_owner_id=owner_id,
            current_user=current_user,
        )
        return {"owner_id": owner_id}

    @app.get("/_test/hidden-resources/{owner_id}")
    async def get_hidden_resource(
        owner_id: int,
        current_user: CurrentUserDep,
    ) -> dict[str, int]:
        verify_resource_ownership(
            resource_owner_id=owner_id,
            current_user=current_user,
            hide_if_unauthorized=True,
        )
        return {"owner_id": owner_id}

    @app.get("/_test/company-only")
    async def company_only(
        current_user: Annotated[User, Depends(require_roles(UserRole.EMPRESA))],
    ) -> dict[str, int]:
        return {"id": current_user.id}

    @app.get("/_test/admin-only")
    async def admin_only(
        current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    ) -> dict[str, int]:
        return {"id": current_user.id}

    return app


@pytest.fixture
def auth_client(auth_app: FastAPI) -> Iterator[TestClient]:
    """Test client for authorization testing."""
    with TestClient(auth_app, raise_server_exceptions=False) as client:
        yield client


def bearer(
    user_id: int,
    role: UserRole = UserRole.TALENTO,
    *,
    expires_in: int = 600,
) -> dict[str, str]:
    """Build the ``Authorization`` header for a token signed by this service."""
    token = create_service_token(
        subject=str(user_id),
        role=role.value,
        secret=TEST_SECRET,
        expires_in=expires_in,
    )
    return {"Authorization": f"Bearer {token}"}


def assert_problem(response: object, *, status: int, code: str) -> None:
    """Assert an RFC 9457 problem-details response with the expected status and code."""
    body = response.json()  # type: ignore[attr-defined]
    assert response.status_code == status  # type: ignore[attr-defined]
    assert response.headers["content-type"].startswith("application/problem+json")  # type: ignore[attr-defined]
    assert body["status"] == status
    assert body["code"] == code


# --------------------------------------------------------------------------- #
# Authentication
# --------------------------------------------------------------------------- #
def test_missing_credential_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/resources/10")

    assert_problem(response, status=401, code="authentication_required")
    assert response.json()["title"] == "Authentication required"


def test_empty_bearer_token_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/me", headers={"Authorization": "Bearer   "})

    assert_problem(response, status=401, code="authentication_required")


def test_forged_signature_returns_401(auth_client: TestClient) -> None:
    forged = create_service_token(
        subject=str(TALENT_ID),
        role=UserRole.ADMIN.value,
        secret="a-different-secret",  # noqa: S106 - wrong key on purpose
    )

    response = auth_client.get("/_test/me", headers={"Authorization": f"Bearer {forged}"})

    assert_problem(response, status=401, code="invalid_credentials")


def test_tampered_payload_returns_401(auth_client: TestClient) -> None:
    token = bearer(TALENT_ID)["Authorization"].removeprefix("Bearer ")
    header, _claims, signature = token.split(".")
    # Re-encode a payload claiming to be the administrator, keeping the original signature.
    import base64
    import json

    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": str(ADMIN_ID), "role": "admin", "exp": 9_999_999_999}).encode()
    ).rstrip(b"=")
    tampered = f"{header}.{payload.decode()}.{signature}"

    response = auth_client.get("/_test/me", headers={"Authorization": f"Bearer {tampered}"})

    assert_problem(response, status=401, code="invalid_credentials")


def test_expired_token_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/me", headers=bearer(TALENT_ID, expires_in=-1))

    assert_problem(response, status=401, code="invalid_credentials")


def test_nonexistent_user_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/me", headers=bearer(12345))

    assert_problem(response, status=401, code="invalid_credentials")


def test_non_numeric_subject_returns_401(auth_client: TestClient) -> None:
    token = create_service_token(
        subject="not-a-user-id",
        role=UserRole.TALENTO.value,
        secret=TEST_SECRET,
    )

    response = auth_client.get("/_test/me", headers={"Authorization": f"Bearer {token}"})

    assert_problem(response, status=401, code="invalid_credentials")


def test_inactive_account_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/me", headers=bearer(INACTIVE_ID))

    assert_problem(response, status=401, code="invalid_credentials")


def test_malformed_authorization_header_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/me", headers={"Authorization": "Token abc"})

    assert_problem(response, status=401, code="authentication_required")


def test_authenticated_user_is_loaded_from_database(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/me", headers=bearer(TALENT_ID))

    assert response.status_code == 200
    # The stored role wins over whatever the token claims.
    assert response.json() == {
        "id": TALENT_ID,
        "email": "talento@skillmatch.test",
        "role": "talento",
    }


def test_token_role_claim_does_not_grant_admin(auth_client: TestClient) -> None:
    # The token says ADMIN, but the stored user is TALENTO.
    response = auth_client.get("/_test/admin-only", headers=bearer(TALENT_ID, UserRole.ADMIN))

    assert_problem(response, status=403, code="permission_denied")


# --------------------------------------------------------------------------- #
# Roles
# --------------------------------------------------------------------------- #
def test_company_role_can_reach_company_endpoint(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/company-only", headers=bearer(COMPANY_ID, UserRole.EMPRESA))

    assert response.status_code == 200
    assert response.json() == {"id": COMPANY_ID}


def test_talent_cannot_reach_company_endpoint(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/company-only", headers=bearer(TALENT_ID))

    assert_problem(response, status=403, code="permission_denied")
    assert response.json()["title"] == "Permission denied"


def test_admin_role_can_reach_admin_endpoint(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/admin-only", headers=bearer(ADMIN_ID, UserRole.ADMIN))

    assert response.status_code == 200
    assert response.json() == {"id": ADMIN_ID}


# --------------------------------------------------------------------------- #
# Ownership
# --------------------------------------------------------------------------- #
def test_own_resource_access_succeeds(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/resources/10", headers=bearer(TALENT_ID))

    assert response.status_code == 200
    assert response.json() == {"owner_id": 10}


def test_cross_account_access_returns_403_forbidden(auth_client: TestClient) -> None:
    # El usuario 20 intenta acceder al recurso perteneciente al usuario 10
    response = auth_client.get("/_test/resources/10", headers=bearer(OTHER_TALENT_ID))

    assert_problem(response, status=403, code="permission_denied")


def test_cross_account_access_returns_404_not_found_when_hidden(
    auth_client: TestClient,
) -> None:
    # El usuario 20 intenta acceder al recurso oculto perteneciente al usuario 10
    response = auth_client.get("/_test/hidden-resources/10", headers=bearer(OTHER_TALENT_ID))

    assert_problem(response, status=404, code="not_found")


def test_admin_can_access_any_resource(auth_client: TestClient) -> None:
    response = auth_client.get("/_test/resources/10", headers=bearer(ADMIN_ID, UserRole.ADMIN))

    assert response.status_code == 200
    assert response.json() == {"owner_id": 10}


def test_admin_can_access_hidden_resource(auth_client: TestClient) -> None:
    response = auth_client.get(
        "/_test/hidden-resources/10", headers=bearer(ADMIN_ID, UserRole.ADMIN)
    )

    assert response.status_code == 200


# --------------------------------------------------------------------------- #
# Dependency override (authorization tested independently of authentication)
# --------------------------------------------------------------------------- #
def test_dependency_override_injects_known_user(auth_app: FastAPI) -> None:
    async def get_fixed_user() -> User:
        return User(id=99, role=UserRole.ADMIN, email="admin@skillmatch.test")

    auth_app.dependency_overrides[get_current_user] = get_fixed_user

    with TestClient(auth_app) as client:
        response = client.get("/_test/resources/10")

    assert response.status_code == 200
    assert response.json() == {"owner_id": 10}
