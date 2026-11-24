"""Reusable FastAPI dependencies.

Dependencies are exposed as ``Annotated`` aliases so route signatures stay short and typed::

    async def handler(settings: SettingsDep) -> ...:

Authentication boundary
-----------------------
``get_current_user`` never trusts anything the client can set freely. The caller must present a
bearer credential (``Authorization: Bearer <token>``) that this service verifies with
:func:`skillmatch.core.security.verify_token`; the identity, role and account status are then
read from the database, so a token can never grant a role the stored user does not have.
"""

from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.core.config import Settings, get_settings
from skillmatch.core.database import async_session_maker
from skillmatch.core.errors import (
    AuthenticationError,
    InvalidCredentialsError,
    NotFoundError,
    PermissionDeniedError,
)
from skillmatch.core.security import InvalidTokenError, verify_token
from skillmatch.modules.identity.models import ACTIVE_ACCOUNT_STATUS, User, UserRole

SettingsDep = Annotated[Settings, Depends(get_settings)]
"""The application settings, resolved once per request."""

bearer_scheme = HTTPBearer(auto_error=False)
"""Parses ``Authorization: Bearer <token>``.

``auto_error=False`` keeps missing credentials in our hands so the response stays RFC 9457.
"""

BearerCredentialsDep = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide a database session for the duration of one request.

    The session is opened from the application's session factory and always closed, even when the
    request fails. Tests replace this dependency with their own session.
    """
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
"""Dependency that yields the per-request database session."""


async def _load_user(session: AsyncSession, subject: str) -> User | None:
    """Return the stored user identified by the token subject.

    A non-numeric subject cannot match any stored user, so it is treated as "not found" and never
    reaches the query.
    """
    if not subject.isdigit():
        return None
    result = await session.execute(select(User).where(User.id == int(subject)))
    return result.scalar_one_or_none()


async def get_current_user(
    credentials: BearerCredentialsDep,
    settings: SettingsDep,
    session: SessionDep,
) -> User:
    """Resolve the authenticated user from a verified bearer token.

    Steps:
        1. A credential must be present, otherwise ``401 authentication_required``.
        2. The token signature and expiry are verified with the service signing secret.
        3. The subject must identify an existing user in the database, otherwise ``401``.
        4. The account must be active, otherwise ``401`` (a disabled account cannot act).

    The session comes from :func:`get_db_session`, so tests can replace it with their own and
    every route shares the same code path.

    Args:
        credentials: Parsed ``Authorization`` header, if any.
        settings: Application settings holding the token signing secret.
        session: Database session used to load the user.

    Returns:
        The stored :class:`User`; its ``role`` is the one used for authorization.

    Raises:
        AuthenticationError: No credential was presented.
        InvalidCredentialsError: The credential is invalid or the account cannot authenticate.
    """
    if credentials is None or not credentials.credentials.strip():
        raise AuthenticationError("Se requiere autenticación mediante Bearer token.")

    try:
        claims = verify_token(credentials.credentials, settings)
    except InvalidTokenError as exc:
        raise InvalidCredentialsError("Credenciales inválidas o expiradas.") from exc

    return _validate_user(await _load_user(session, claims.subject))


def _validate_user(user: User | None) -> User:
    """Ensure the stored user exists and may authenticate."""
    if user is None:
        # Same generic message as a forged token: it must not reveal which users exist.
        raise InvalidCredentialsError("Credenciales inválidas o expiradas.")
    if user.status != ACTIVE_ACCOUNT_STATUS:
        raise InvalidCredentialsError("La cuenta no está activa.")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
"""Dependencia inyectable para obtener el usuario autenticado."""


def require_roles(*allowed_roles: UserRole) -> Callable[[User], Awaitable[User]]:
    """Build a dependency that only lets the given roles through.

    Args:
        *allowed_roles: Roles allowed to reach the endpoint.

    Returns:
        A dependency returning the authenticated user when their stored role is allowed, and
        raising ``403 permission_denied`` otherwise.
    """

    async def _dependency(current_user: CurrentUserDep) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError("No tienes permiso para acceder a este recurso.")
        return current_user

    return _dependency


def verify_resource_ownership(
    resource_owner_id: int,
    current_user: User,
    *,
    hide_if_unauthorized: bool = False,
) -> None:
    """Verifica que el usuario actual sea propietario del recurso o tenga rol ADMIN.

    - Si `hide_if_unauthorized=True` y no tiene permiso: lanza `NotFoundError` (HTTP 404)
      para evitar la enumeración de recursos.
    - De lo contrario: lanza `PermissionDeniedError` (HTTP 403).
    """
    if current_user.role == UserRole.ADMIN:
        return

    if current_user.id != resource_owner_id:
        if hide_if_unauthorized:
            raise NotFoundError("Recurso no encontrado.")
        raise PermissionDeniedError("No tienes permiso para acceder a este recurso.")


__all__: Sequence[str] = (
    "ACTIVE_ACCOUNT_STATUS",
    "CurrentUserDep",
    "SessionDep",
    "SettingsDep",
    "get_current_user",
    "get_db_session",
    "require_roles",
    "verify_resource_ownership",
)
