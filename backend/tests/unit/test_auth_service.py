
"""Unit tests for the identity authentication service."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.core.config import Settings
from skillmatch.modules.identity.errors import EmailAlreadyRegisteredError
from skillmatch.modules.identity.passwords import PasswordHasher
from skillmatch.modules.identity.schemas import PublicRole, RegisterRequest
from skillmatch.modules.identity.service import AuthService

TEST_PASSWORD = "test-" + "value-" + "123"

@pytest.mark.anyio
async def test_register_rolls_back_when_email_unique_constraint_fails(
    settings: Settings,
) -> None:
    """Translate a concurrent unique-email conflict and roll back the transaction."""
    session = AsyncMock(spec=AsyncSession)
    query_result = MagicMock()
    query_result.scalar_one_or_none.return_value = None
    session.execute.return_value = query_result

    hasher = AsyncMock(spec=PasswordHasher)
    hasher.hash_async.return_value = "scrypt-test-hash"

    integrity_error = IntegrityError(
        "INSERT INTO users",
        {"email": "candidate@example.com"},
        Exception("unique constraint violation"),
    )
    session.commit.side_effect = integrity_error

    service = AuthService(
        session=session,
        hasher=hasher,
        settings=settings,
    )
    data = RegisterRequest(
        email="candidate@example.com",
        password=TEST_PASSWORD,
        role=PublicRole.TALENTO,
    )

    with pytest.raises(EmailAlreadyRegisteredError) as exc_info:
        await service.register(data)

    session.execute.assert_awaited_once()
    hasher.hash_async.assert_awaited_once_with(data.password)
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.rollback.assert_awaited_once()
    assert exc_info.value.__cause__ is integrity_error
