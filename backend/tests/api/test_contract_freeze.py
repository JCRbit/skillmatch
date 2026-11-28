"""The published API contract and the freeze policy that protects it.

The contract is frozen as data, not as prose: ``docs/api/openapi-v1.json`` is a copy of the
generated document, and every change to it goes through a pull request. These tests keep the
three artefacts in step and fail when the policy is broken:

- the frozen document against the running application,
- the consumer examples against the frozen document,
- the compatibility check itself, which must catch a breaking change and allow an additive one.
"""

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from fastapi.testclient import TestClient

from skillmatch.app import create_app
from skillmatch.core.config import Environment, Settings

BACKEND = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND.parent
FROZEN_CONTRACT = REPO_ROOT / "docs" / "api" / "openapi-v1.json"
EXAMPLES = REPO_ROOT / "docs" / "api" / "examples" / "operations.json"
GENERATED_CONTRACT = BACKEND / "openapi.json"


def _load_script(name: str) -> ModuleType:
    """Import a script from ``backend/scripts`` without turning it into a package."""
    path = BACKEND / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None, path
    assert spec.loader is not None, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compatibility = _load_script("check_contract_compatibility")
examples = _load_script("generate_contract_examples")

Document = dict[str, Any]


def _load(path: Path) -> Document:
    document: Document = json.loads(path.read_text(encoding="utf-8"))
    return document


def _generated() -> Document:
    generated: Document = json.loads(
        json.dumps(create_app(Settings(environment=Environment.TEST)).openapi())
    )
    return generated


def test_the_frozen_contract_matches_the_application() -> None:
    """The published copy is the contract: it must be the document the code produces."""
    assert _load(FROZEN_CONTRACT) == _generated(), (
        "docs/api/openapi-v1.json is stale. Run: uv run python scripts/export_openapi.py, then "
        "copy backend/openapi.json over docs/api/openapi-v1.json"
    )


def test_the_generated_contract_is_the_frozen_one() -> None:
    """``backend/openapi.json`` and the frozen copy never diverge."""
    assert _load(GENERATED_CONTRACT) == _load(FROZEN_CONTRACT)


def test_the_examples_match_the_frozen_contract() -> None:
    """The consumer examples are generated from the contract, so they cannot drift."""
    expected = examples.build_examples(_load(FROZEN_CONTRACT))

    assert _load(EXAMPLES) == json.loads(json.dumps(expected)), (
        "docs/api/examples/operations.json is stale. Run: "
        "uv run python scripts/generate_contract_examples.py"
    )


def test_every_operation_has_an_example() -> None:
    """A consumer can mock every endpoint, not just the ones that came to mind."""
    operations = _load(EXAMPLES)["operations"]

    assert len(operations) == len(compatibility._operations(_load(FROZEN_CONTRACT)))
    assert all("response" in entry or entry["method"] == "DELETE" for entry in operations.values())


def test_the_examples_carry_no_identity_fields() -> None:
    """The published examples must not teach a consumer to expect identity data."""
    identity = {"user_id", "candidate_id", "password_hash", "role_id"}
    projection = _load(EXAMPLES)["operations"]["GET /api/v1/candidates/{candidate_id}"]

    assert not identity & set(projection["response"]["body"])


def test_the_policy_document_states_the_freeze() -> None:
    """The policy is written down where a consumer looks for it."""
    policy = (FROZEN_CONTRACT.parent / "README.md").read_text(encoding="utf-8").lower()

    for phrase in ("freeze", "breaking", "vanessa", "api/v2"):
        assert phrase in policy, phrase


def test_the_contract_covers_the_m2_flow_that_exists() -> None:
    """C-01 freezes what the sprint delivered; the rest arrives with its own task."""
    operations = set(compatibility._operations(_load(FROZEN_CONTRACT)))

    assert ("/api/v1/candidates/{candidate_id}", "get") in operations
    assert ("/api/v1/candidates/me/consents/{purpose}", "put") in operations
    assert ("/api/v1/jobs", "post") in operations


def test_the_contract_declares_the_version_prefix_and_security() -> None:
    """Consumers can generate a client without guessing the version or the auth scheme."""
    document = _load(FROZEN_CONTRACT)

    assert document["info"]["version"]
    assert any(path.startswith("/api/v1/") for path in document["paths"])
    assert document["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"


# --------------------------------------------------------------- compatibility
def test_an_unchanged_contract_is_compatible() -> None:
    """Comparing a document with itself reports nothing."""
    document = _load(FROZEN_CONTRACT)

    assert compatibility.compare(document, copy.deepcopy(document)) == []


def test_a_new_optional_field_is_compatible() -> None:
    """Adding a field a client may ignore does not break it."""
    base = _load(FROZEN_CONTRACT)
    current = copy.deepcopy(base)
    schema = current["components"]["schemas"]["CandidateProjection"]
    schema["properties"]["headline"] = {"type": "string"}

    assert compatibility.compare(base, current) == []


def test_a_removed_endpoint_is_breaking() -> None:
    """A client calling it would start receiving 404."""
    base = _load(FROZEN_CONTRACT)
    current = copy.deepcopy(base)
    del current["paths"]["/api/v1/jobs"]

    problems = compatibility.compare(base, current)

    assert any("removed operation" in problem for problem in problems)


def test_a_removed_response_status_is_breaking() -> None:
    """A documented error a client handles must not disappear silently."""
    base = _load(FROZEN_CONTRACT)
    current = copy.deepcopy(base)
    del current["paths"]["/api/v1/auth/login"]["post"]["responses"]["503"]

    problems = compatibility.compare(base, current)

    assert any("removed response 503" in problem for problem in problems)


def test_a_removed_field_is_breaking() -> None:
    """A client reading the field would break on the new payload."""
    base = _load(FROZEN_CONTRACT)
    current = copy.deepcopy(base)
    del current["components"]["schemas"]["CandidateProjection"]["properties"]["city"]

    problems = compatibility.compare(base, current)

    assert any("removed field 'city'" in problem for problem in problems)


def test_a_removed_enum_value_is_breaking() -> None:
    """A value the client accepts today must keep being accepted."""
    base = _load(FROZEN_CONTRACT)
    current = copy.deepcopy(base)
    current["components"]["schemas"]["SkillLevel"]["enum"] = ["beginner", "advanced"]

    problems = compatibility.compare(base, current)

    assert any("removed enum value" in problem for problem in problems)


def test_a_field_that_stops_being_required_is_compatible() -> None:
    """Loosening a requirement never breaks a client."""
    base = _load(FROZEN_CONTRACT)
    current = copy.deepcopy(base)
    current["components"]["schemas"]["CandidateProjection"]["required"] = []

    assert compatibility.compare(base, current) == []


def test_a_field_that_becomes_required_is_breaking() -> None:
    """A client that omitted it would start receiving 422."""
    base = _load(FROZEN_CONTRACT)
    current = copy.deepcopy(base)
    current["components"]["schemas"]["CandidateProjection"]["required"] = [
        *current["components"]["schemas"]["CandidateProjection"].get("required", []),
        "city",
    ]

    problems = compatibility.compare(base, current)

    assert any("became required" in problem for problem in problems)


def test_the_command_reports_a_breaking_change(tmp_path: Path) -> None:
    """The CI step fails, with a message a reviewer can act on, when the contract narrows."""
    base = _load(FROZEN_CONTRACT)
    narrowed = copy.deepcopy(base)
    del narrowed["paths"]["/api/v1/candidates/{candidate_id}"]
    base_path = tmp_path / "base.json"
    current_path = tmp_path / "current.json"
    base_path.write_text(json.dumps(base), encoding="utf-8")
    current_path.write_text(json.dumps(narrowed), encoding="utf-8")

    exit_code = compatibility.main(["--base", str(base_path), "--current", str(current_path)])

    assert exit_code == 1


def test_the_command_passes_when_the_contract_grows(tmp_path: Path) -> None:
    """An additive change is the normal case and must not block a pull request."""
    base = _load(FROZEN_CONTRACT)
    grown = copy.deepcopy(base)
    grown["paths"]["/api/v1/interests"] = {"post": {"responses": {"201": {"description": "ok"}}}}
    base_path = tmp_path / "base.json"
    current_path = tmp_path / "current.json"
    base_path.write_text(json.dumps(base), encoding="utf-8")
    current_path.write_text(json.dumps(grown), encoding="utf-8")

    assert compatibility.main(["--base", str(base_path), "--current", str(current_path)]) == 0


def test_a_served_contract_is_the_frozen_one(client: TestClient) -> None:
    """What ``/openapi.json`` serves is what the repository publishes."""
    assert client.get("/openapi.json").json() == _load(FROZEN_CONTRACT)


@pytest.mark.parametrize("path", ["/api/v1/candidates/{candidate_id}", "/api/v1/jobs"])
def test_the_frozen_operations_keep_their_security(path: str) -> None:
    """A frozen operation cannot lose its bearer requirement without a breaking change."""
    operations = compatibility._operations(_load(FROZEN_CONTRACT))

    assert any(
        key[0] == path and operation.get("security") for key, operation in operations.items()
    )
