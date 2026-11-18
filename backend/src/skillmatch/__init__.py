"""SkillMatch backend package.

Competency-based matching between junior talent and companies. See
``docs/ARCHITECTURE.md`` for the architectural overview.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("skillmatch")
except PackageNotFoundError:  # pragma: no cover - only when running from a bare checkout
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
