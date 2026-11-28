"""Generate the consumer-facing examples of the published contract.

Usage, from ``backend/``::

    uv run python scripts/generate_contract_examples.py
    uv run python scripts/generate_contract_examples.py --check

The output is ``docs/api/examples/operations.json``: one entry per operation of
``docs/api/openapi-v1.json`` with a sample request body and a sample success response, built from
the schemas the contract declares. The frontend uses them as mocks, and a test keeps them in step
with the frozen document so they cannot drift.

Every value is invented: no real person, company or offer. Sample strings that must look like an
identifier carry the ``sample`` prefix on purpose.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_CONTRACT = REPO_ROOT / "docs" / "api" / "openapi-v1.json"
EXAMPLES = REPO_ROOT / "docs" / "api" / "examples" / "operations.json"

Document = dict[str, Any]

_HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
_MAX_DEPTH = 6

# Sample values per field name. Anything not listed falls back to the schema type.
_SAMPLES: dict[str, object] = {
    "access_token": "sample-bearer-token",
    "city": "Sample City",
    "company_id": 7,
    "contract_type": "full_time",
    "created_at": "2026-01-15T09:30:00+00:00",
    "description": "Sample description for the contract example.",
    "display_name": "Sample Candidate",
    "email": "candidate@example.test",
    "expires_in": 3600,
    "granted": True,
    "granted_at": "2026-01-15T09:30:00+00:00",
    "id": 1,
    "languages": ["spanish", "english"],
    "level": "intermediate",
    "location": "Sample City",
    "name": "Sample name",
    "password": "sample-password-12",
    "policy_version": "2026-01",
    "purpose": "discovery",
    "revoked_at": None,
    "role": "talento",
    "salary_currency": "EUR",
    "salary_max": 32000,
    "salary_min": 24000,
    "seniority": "junior",
    "summary": "Sample summary written for the contract example.",
    "title": "Sample vacancy title",
    "token_type": "bearer",
    "updated_at": "2026-01-15T09:30:00+00:00",
    "website": "https://example.test",
    "work_mode": "hybrid",
    "years_experience": 1,
}


def _load(path: Path) -> Document:
    """Read a JSON document from ``path``."""
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(document: Document, schema: object, depth: int = 0) -> object:
    """Return the sample value for ``schema``, following ``$ref`` when present."""
    if depth > _MAX_DEPTH or not isinstance(schema, dict):
        return None

    reference = schema.get("$ref")
    if isinstance(reference, str) and reference.startswith("#/components/schemas/"):
        name = reference.rsplit("/", 1)[-1]
        target = (document.get("components") or {}).get("schemas", {}).get(name)
        return _resolve(document, target, depth + 1)

    for variant in schema.get("anyOf") or schema.get("oneOf") or []:
        if isinstance(variant, dict) and variant.get("type") != "null":
            return _resolve(document, variant, depth + 1)

    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return enum[0]

    schema_type = schema.get("type")
    if schema_type == "object" or "properties" in schema:
        return _object(document, schema, depth)
    if schema_type == "array":
        item = _resolve(document, schema.get("items") or {}, depth + 1)
        return [item]
    if schema_type == "integer":
        return 1
    if schema_type == "number":
        return 1.0
    if schema_type == "boolean":
        return True
    if schema_type == "null":
        return None
    return "sample"


def _object(document: Document, schema: Document, depth: int) -> Document:
    """Return a sample object with a value for every declared property."""
    properties = schema.get("properties") or {}
    sample: Document = {}
    for name, subschema in properties.items():
        sample[name] = (
            _SAMPLES[name] if name in _SAMPLES else _resolve(document, subschema, depth + 1)
        )
    return sample


def _success_status(operation: Document) -> str | None:
    """Return the success status of an operation: ``2xx``, preferring the documented one."""
    responses = operation.get("responses") or {}
    for status in sorted(responses):
        if status.startswith("2") and status != "204":
            return status
    return None


def build_examples(document: Document) -> Document:
    """Return one sample request and response per operation of ``document``."""
    examples: Document = {}
    for path, item in sorted((document.get("paths") or {}).items()):
        if not isinstance(item, dict):
            continue
        for method, operation in sorted(item.items()):
            if method.lower() not in _HTTP_METHODS or not isinstance(operation, dict):
                continue

            entry: Document = {"method": method.upper(), "path": path}

            body = (operation.get("requestBody") or {}).get("content") or {}
            for media_type, media in body.items():
                if isinstance(media, dict) and "schema" in media:
                    entry["request"] = {
                        "media_type": media_type,
                        "body": _resolve(document, media["schema"]),
                    }
                    break

            status = _success_status(operation)
            if status is not None:
                content = (operation["responses"][status] or {}).get("content") or {}
                for media_type, media in content.items():
                    if isinstance(media, dict) and "schema" in media:
                        entry["response"] = {
                            "status": int(status),
                            "media_type": media_type,
                            "body": _resolve(document, media["schema"]),
                        }
                        break

            examples[f"{method.upper()} {path}"] = entry
    return {"contract": "docs/api/openapi-v1.json", "operations": examples}


def main(argv: list[str] | None = None) -> int:
    """Regenerate the examples, or verify them with ``--check``."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--check", action="store_true", help="fail if the examples are stale")
    args = parser.parse_args(argv)

    expected = build_examples(_load(FROZEN_CONTRACT))

    if args.check:
        current = _load(EXAMPLES) if EXAMPLES.exists() else {}
        if current != json.loads(json.dumps(expected)):
            sys.stderr.write(
                "docs/api/examples/operations.json is stale; run "
                "scripts/generate_contract_examples.py\n"
            )
            return 1
        sys.stdout.write("OK: the contract examples match the published contract\n")
        return 0

    EXAMPLES.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES.write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sys.stdout.write(f"Wrote {EXAMPLES}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
