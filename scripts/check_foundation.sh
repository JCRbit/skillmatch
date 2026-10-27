#!/usr/bin/env bash
set -euo pipefail

# Simple consistency check for the documentation pack; no app/runtime dependencies needed.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"
required=(AGENTS.md START_HERE.md docs/PROJECT_CHARTER.md docs/REQUIREMENTS.md docs/ARCHITECTURE.md docs/TECH_STACK.md docs/TEAM_WORKING_AGREEMENT.md docs/legacy-audit/README.md AUDIT_FIRST_PROMPT.md)
missing=0
for f in "${required[@]}"; do
  if [[ ! -f "$f" ]]; then echo "MISSING: $f"; missing=1; fi
done
if [[ -f docs/REQUIREMENTS.md ]] && ! grep -q 'FR-020' docs/REQUIREMENTS.md; then echo 'Missing requirement FR-020'; missing=1; fi
if [[ -f AGENTS.md ]] && ! grep -qi 'read-only' AGENTS.md; then echo 'Missing legacy read-only rule'; missing=1; fi
if (( missing != 0 )); then exit 1; fi
echo 'Foundation consistency checks passed.'
