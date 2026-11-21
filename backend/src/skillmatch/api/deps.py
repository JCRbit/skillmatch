"""Reusable FastAPI dependencies.

Dependencies are exposed as ``Annotated`` aliases so route signatures stay short and typed::

    async def handler(settings: SettingsDep) -> ...:
"""

from typing import Annotated

from fastapi import Depends, Header

from skillmatch.core.config import Settings, get_settings
from skillmatch.core.errors import (
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
)
from skillmatch.modules.identity.models import User, UserRole

SettingsDep = Annotated[Settings, Depends(get_settings)]
"""The application settings, resolved once per request."""


async def get_current_user(
    x_user_id: Annotated[int | None, Header()] = None,
) -> User:
    """Resuelve el usuario autenticado a partir de las cabeceras HTTP."""
    if x_user_id is None:
        raise AuthenticationError("Se requiere la cabecera X-User-Id.")

    return User(
        id=x_user_id,
        role=UserRole.TALENTO,
        email=f"user_{x_user_id}@skillmatch.test",
    )


CurrentUserDep = Annotated[User, Depends(get_current_user)]
"""Dependencia inyectable para obtener el usuario autenticado."""


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
