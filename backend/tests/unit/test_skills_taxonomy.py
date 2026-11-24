from skillmatch.modules.skills.taxonomy import Skill, load_taxonomy


def test_load_taxonomy_returns_all_80_skills() -> None:
    skills = load_taxonomy()

    assert len(skills) == 80
    assert all(isinstance(skill, Skill) for skill in skills)


def test_canonical_ids_are_unique() -> None:
    skills = load_taxonomy()
    canonical_ids = [skill.canonical_id for skill in skills]

    assert len(canonical_ids) == len(set(canonical_ids))


def test_aliases_are_loaded_as_individual_values() -> None:
    skills = load_taxonomy()
    javascript = next(skill for skill in skills if skill.canonical_id == "javascript")

    assert javascript.aliases == ("JavaScript", "JS")


def test_java_and_javascript_are_independent_skills() -> None:
    skills = load_taxonomy()
    skills_by_id = {skill.canonical_id: skill for skill in skills}

    assert "java" in skills_by_id
    assert "javascript" in skills_by_id
    assert skills_by_id["java"].canonical_id != (skills_by_id["javascript"].canonical_id)


def test_esco_optional_fields_preserve_missing_values() -> None:
    skills = load_taxonomy()
    skills_by_id = {skill.canonical_id: skill for skill in skills}

    python_skill = skills_by_id["python"]
    assert python_skill.esco_label == "Python (programación informática)"
    assert python_skill.esco_uri is not None
    assert python_skill.esco_concept_type is None
    assert python_skill.esco_concept_state is None

    go_skill = skills_by_id["go"]
    assert go_skill.esco_label is None
    assert go_skill.esco_uri is None
    assert go_skill.esco_concept_type is None
    assert go_skill.esco_concept_state is None
    assert go_skill.esco_status == "PENDING_VERIFICATION"
