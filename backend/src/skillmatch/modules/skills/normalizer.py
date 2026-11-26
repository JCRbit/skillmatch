"""Normalize skill names and resolve aliases to canonical identifiers."""

import re
from collections.abc import Iterable

from skillmatch.modules.skills.taxonomy import Skill


class AliasCollisionError(ValueError):
    """Raised when an alias maps to multiple canonical skills."""


def normalize_alias(value: str) -> str:
    """Normalize an alias without changing accents or punctuation."""
    return re.sub(r"\s+", " ", value.strip().casefold())


def build_alias_index(skills: Iterable[Skill]) -> dict[str, str]:
    """Build an exact normalized alias-to-canonical-ID index."""
    alias_index: dict[str, str] = {}

    for skill in skills:
        aliases = (skill.skill, *skill.aliases)

        for alias in aliases:
            normalized = normalize_alias(alias)

            if not normalized:
                continue

            existing_id = alias_index.get(normalized)

            if existing_id is not None and existing_id != skill.canonical_id:
                raise AliasCollisionError(
                    f"Alias '{alias}' maps to both '{existing_id}' and '{skill.canonical_id}'."
                )

            alias_index[normalized] = skill.canonical_id

    return alias_index


def resolve_alias(value: str, alias_index: dict[str, str]) -> str | None:
    """Resolve an exact normalized alias to its canonical ID."""
    return alias_index.get(normalize_alias(value))
