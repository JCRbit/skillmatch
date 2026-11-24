import pytest

from skillmatch.modules.skills.normalizer import (
    AliasCollisionError,
    build_alias_index,
    normalize_alias,
    resolve_alias,
)
from skillmatch.modules.skills.taxonomy import Skill, load_taxonomy


@pytest.fixture
def alias_index() -> dict[str, str]:
    return build_alias_index(load_taxonomy())


def test_normalize_alias_case_and_whitespace() -> None:
    assert normalize_alias("  JAVA   SCRIPT  ") == "java script"


def test_normalize_alias_preserves_accents_and_punctuation() -> None:
    assert normalize_alias("  Gestión Ágil  ") == "gestión ágil"
    assert normalize_alias("C++") == "c++"


def test_resolve_registered_aliases(alias_index: dict[str, str]) -> None:
    assert resolve_alias("PYTHON", alias_index) == "python"
    assert resolve_alias("JS", alias_index) == "javascript"
    assert resolve_alias("TypeScript", alias_index) == "typescript"


def test_java_and_javascript_are_not_confused(
    alias_index: dict[str, str],
) -> None:
    assert resolve_alias("Java", alias_index) == "java"
    assert resolve_alias("JavaScript", alias_index) == "javascript"


def test_unknown_or_partial_alias_returns_none(
    alias_index: dict[str, str],
) -> None:
    assert resolve_alias("unknown skill", alias_index) is None
    assert resolve_alias("Java Script", alias_index) is None


def test_duplicate_alias_within_same_skill_is_allowed() -> None:
    skill = Skill(
        category_id="1",
        category="Test",
        canonical_id="python",
        skill="Python",
        aliases=("PYTHON", " Python "),
        operational_description="Test skill",
        esco_label=None,
        esco_uri=None,
        esco_concept_type=None,
        esco_concept_state=None,
        esco_status="PENDING_VERIFICATION",
    )

    assert build_alias_index([skill]) == {"python": "python"}


def test_alias_collision_between_different_skills_raises_error() -> None:
    first = Skill(
        category_id="1",
        category="Test",
        canonical_id="first",
        skill="First skill",
        aliases=("Shared alias",),
        operational_description="First test skill",
        esco_label=None,
        esco_uri=None,
        esco_concept_type=None,
        esco_concept_state=None,
        esco_status="PENDING_VERIFICATION",
    )
    second = Skill(
        category_id="1",
        category="Test",
        canonical_id="second",
        skill="Second skill",
        aliases=(" shared   ALIAS ",),
        operational_description="Second test skill",
        esco_label=None,
        esco_uri=None,
        esco_concept_type=None,
        esco_concept_state=None,
        esco_status="PENDING_VERIFICATION",
    )

    with pytest.raises(AliasCollisionError):
        build_alias_index([first, second])
