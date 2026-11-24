"""Use cases of the identity module: public registration and credential login.

The service never decides *who the caller is* for later requests: that is the job of
:func:`skillmatch.api.deps.get_current_user`, which verifies the bearer token issued here and then
reloads the account from the database. The service only creates accounts and exchanges valid
credentials for a signed token.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.core.config import Settings
from skillmatch.core.errors import InvalidCredentialsError
from skillmatch.core.security import create_service_token
from skillmatch.modules.identity.errors import (
    AuthenticationUnavailableError,
    EmailAlreadyRegisteredError,
)
from skillmatch.modules.identity.models import ACTIVE_ACCOUNT_STATUS, User
from skillmatch.modules.identity.passwords import PasswordHasher
from skillmatch.modules.identity.schemas import LoginRequest, RegisterRequest

logger = logging.getLogger(__name__)

_INVALID_CREDENTIALS = "Credenciales inválidas."
"""One message for every login failure, so it never reveals which part was wrong."""


@dataclass(frozen=True, slots=True)
class IssuedToken:
    """A freshly issued access token and the account it belongs to.

    Attributes:
        access_token: The signed bearer token.
        expires_in: Lifetime in seconds.
        user: The authenticated account, as stored in the database.
    """

    access_token: str
    expires_in: int
    user: User


def _utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(UTC)


class AuthService:
    """Registers accounts and exchanges valid credentials for access tokens."""

    def __init__(
        self,
        session: AsyncSession,
        hasher: PasswordHasher,
        settings: Settings,
        *,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        """Wire the service to its collaborators.

        Args:
            session: Database session of the current request.
            hasher: Password hashing.
            settings: Application settings; the signing secret and token lifetime come from here.
            clock: Time source for ``last_login_at``; replaceable in tests.
        """
        self._session = session
        self._hasher = hasher
        self._settings = settings
        self._clock = clock

    async def register(self, data: RegisterRequest) -> User:
        """Create an account through the public registration flow.

        The account is created ``active`` with the requested public role. The password is stored
        only as a scrypt hash.

        Raises:
            EmailAlreadyRegisteredError: If the email is already taken.
        """
        if await self._find_by_email(data.email) is not None:
            raise EmailAlreadyRegisteredError

        user = User(
            email=data.email,
            password_hash=await self._hasher.hash_async(data.password),
            role=data.role.to_user_role(),
            status=ACTIVE_ACCOUNT_STATUS,
        )
        self._session.add(user)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            # A concurrent registration won the race for the unique email index.
            await self._session.rollback()
            raise EmailAlreadyRegisteredError from exc
        return user

    async def login(self, data: LoginRequest) -> IssuedToken:
        """Verify credentials and issue an access token.

        Unknown email, wrong password, an account without a password and a non-active account all
        raise the same error, and a password check always runs (against a dummy hash when there
        is no account), so neither the message nor the timing reveals which accounts exist.

        Raises:
            AuthenticationUnavailableError: If no signing secret is configured.
            InvalidCredentialsError: If the credentials are not valid for an active account.
        """
        secret = self._settings.auth_service_secret.get_secret_value()
        if not secret:
            logger.error("Login refused: SKILLMATCH_AUTH_SERVICE_SECRET is not configured.")
            raise AuthenticationUnavailableError

        user = await self._find_by_email(data.email)
        stored_hash = user.password_hash if user is not None else None
        hash_to_verify = stored_hash

        if hash_to_verify is None:
            hash_to_verify = await self._hasher.dummy_hash_async()

        matches = await self._hasher.verify_async(hash_to_verify, data.password)

        if user is None or stored_hash is None or not matches:
            raise InvalidCredentialsError(_INVALID_CREDENTIALS)
        if user.status != ACTIVE_ACCOUNT_STATUS:
            raise InvalidCredentialsError(_INVALID_CREDENTIALS)

        if self._hasher.needs_rehash(stored_hash):
            user.password_hash = await self._hasher.hash_async(data.password)
        user.last_login_at = self._clock()
        await self._session.commit()

        expires_in = self._settings.auth_token_ttl_seconds
        token = create_service_token(
            subject=str(user.id),
            role=user.role.value,
            secret=secret,
            expires_in=expires_in,
        )
        return IssuedToken(access_token=token, expires_in=expires_in, user=user)

    async def _find_by_email(self, email: str) -> User | None:
        """Return the account registered with this (normalised) email, if any."""
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
