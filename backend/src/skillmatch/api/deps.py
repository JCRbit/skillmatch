"""Reusable FastAPI dependencies.

Dependencies are exposed as ``Annotated`` aliases so route signatures stay short and typed::

    async def handler(settings: SettingsDep) -> ...:
"""

from typing import Annotated

from fastapi import Depends

from skillmatch.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
"""The application settings, resolved once per request."""
