"""HTTP endpoints for registration, login and the authenticated account.

==========================  =============  ===============================================
Endpoint                    Access         Purpose
==========================  =============  ===============================================
``POST /auth/register``     public         Create a ``talento`` or ``empresa`` account.
``POST /auth/login``        public         Exchange email and password for an access token.
``GET  /auth/me``           authenticated  The caller's own account, read from the database.
==========================  =============  ===============================================

The identity and role of later requests always come from the verified token and the database
(:func:`skillmatch.api.deps.get_current_user`), never from anything the client sends freely.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from skillmatch.api.deps import CurrentUserDep, SessionDep, SettingsDep
from skillmatch.api.problems import problem_responses
from skillmatch.modules.identity.passwords import PasswordHasher
from skillmatch.modules.identity.schemas import (
    AuthenticatedUser,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)
from skillmatch.modules.identity.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@lru_cache
def get_password_hasher() -> PasswordHasher:
    """Return the process-wide password hasher. Tests override this dependency."""
    return PasswordHasher()


PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
"""The password hasher, with production cost parameters."""


def get_auth_service(
    session: SessionDep, settings: SettingsDep, hasher: PasswordHasherDep
) -> AuthService:
    """Build the :class:`AuthService` for one request."""
    return AuthService(session, hasher, settings)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
"""The authentication service of the current request."""


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Create an account",
    responses=problem_responses(409, 422),
)
async def register(body: RegisterRequest, service: AuthServiceDep) -> UserRead:
    """Register a candidate (`talento`) or a company (`empresa`).

    Administrators cannot be created here: the `admin` role is rejected. The account starts
    `active`, and the password is stored only as a scrypt hash.
    """
    return UserRead.model_validate(await service.register(body))


@router.post(
    "/login",
    summary="Exchange credentials for an access token",
    responses=problem_responses(401, 422, 503),
)
async def login(body: LoginRequest, service: AuthServiceDep, response: Response) -> TokenResponse:
    """Authenticate with email and password.

    Returns a short-lived bearer token together with the identity and role stored in the
    database. The error is identical for an unknown email, a wrong password and an inactive
    account.
    """
    issued = await service.login(body)
    # Tokens must never be stored by browsers or intermediaries (RFC 6749, section 5.1).
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return TokenResponse(
        access_token=issued.access_token,
        expires_in=issued.expires_in,
        user=AuthenticatedUser(id=issued.user.id, email=issued.user.email, role=issued.user.role),
    )


@router.get("/me", summary="The authenticated account", responses=problem_responses(401))
async def read_me(current_user: CurrentUserDep) -> UserRead:
    """Return the account behind the bearer token."""
    return UserRead.model_validate(current_user)
