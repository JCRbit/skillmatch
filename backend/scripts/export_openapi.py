"""Write (or check) the OpenAPI contract ``backend/openapi.json``.

Usage, from ``backend/``::

    uv run python scripts/export_openapi.py            # regenerate the file
    uv run python scripts/export_openapi.py --check    # fail if the file is stale (CI-friendly)

Run it with a clean environment: the document is built from the default test settings, so
variables such as ``SKILLMATCH_APP_NAME`` would change its title.
"""

import argparse
import json
import sys
from pathlib import Path

from skillmatch.app import create_app
from skillmatch.core.config import Environment, Settings

CONTRACT = Path(__file__).resolve().parents[1] / "openapi.json"


def build_contract() -> str:
    """Return the OpenAPI document of the application as formatted JSON."""
    schema = create_app(Settings(environment=Environment.TEST)).openapi()
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    """Regenerate the contract, or verify it with ``--check``."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--check", action="store_true", help="fail if openapi.json is stale")
    args = parser.parse_args()

    expected = build_contract()
    if args.check:
        current = CONTRACT.read_text(encoding="utf-8") if CONTRACT.exists() else ""
        if json.loads(current or "null") != json.loads(expected):
            sys.stderr.write("openapi.json is stale; run scripts/export_openapi.py\n")
            return 1
        return 0

    CONTRACT.write_text(expected, encoding="utf-8")
    sys.stdout.write(f"Wrote {CONTRACT}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
