"""Public API for the skills taxonomy and alias resolution."""

from skillmatch.modules.skills.normalizer import (
    AliasCollisionError,
    build_alias_index,
    normalize_alias,
    resolve_alias,
)
from skillmatch.modules.skills.taxonomy import (
    Skill,
    TaxonomyError,
    load_taxonomy,
)

__all__ = [
    "AliasCollisionError",
    "Skill",
    "TaxonomyError",
    "build_alias_index",
    "load_taxonomy",
    "normalize_alias",
    "resolve_alias",
]
