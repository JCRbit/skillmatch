#!/usr/bin/env bash
set -euo pipefail

# Read-only inventory helper. It writes only under the *new project* output path.
# Usage from new repo root: scripts/legacy_inventory.sh /absolute/path/to/legacy [output_dir]

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/legacy [output_dir]" >&2
  exit 2
fi
LEGACY="$(cd "$1" && pwd -P)"
OUT="${2:-docs/legacy-audit/generated}"
mkdir -p "$OUT"
OUT_ABS="$(mkdir -p "$OUT" && cd "$OUT" && pwd -P)"

case "$OUT_ABS/" in
  "$LEGACY"/*) echo "ERROR: output directory is inside legacy; aborting." >&2; exit 3 ;;
esac

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$OUT_ABS/inventory-$STAMP.md"
{
  echo "# Automated legacy inventory (static only)"
  echo
  echo "- Generated UTC: $STAMP"
  echo "- Legacy absolute path: $LEGACY"
  echo "- Git root: $(git -C "$LEGACY" rev-parse --show-toplevel 2>/dev/null || echo UNKNOWN)"
  echo "- Branch: $(git -C "$LEGACY" branch --show-current 2>/dev/null || echo UNKNOWN)"
  echo "- Commit SHA: $(git -C "$LEGACY" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
  echo "- Remote URLs: redacted by policy; inspect `git remote -v` locally and record approved URL manually."
  echo
  echo "## Worktree status"
  echo '```text'
  git -C "$LEGACY" status --short 2>/dev/null || true
  echo '```'
  echo
  echo "## Tracked file counts by extension"
  echo '```text'
  git -C "$LEGACY" ls-files 2>/dev/null | awk '
    { n=$0; sub(/^.*\//,"",n); if (n !~ /\./) ext="[no extension]"; else { sub(/^.*\./,"",n); ext="." n } count[ext]++ }
    END { for (e in count) print count[e], e }
  ' | sort -nr | head -80
  echo '```'
  echo
  echo "## Top-level tracked paths"
  echo '```text'
  git -C "$LEGACY" ls-files 2>/dev/null | awk -F/ '{print $1}' | sort -u | head -150
  echo '```'
  echo
  echo "## Large tracked files (names only; thresholds >5 MiB)"
  echo '```text'
  git -C "$LEGACY" ls-files -z 2>/dev/null | while IFS= read -r -d '' f; do
    if [[ -f "$LEGACY/$f" ]]; then
      size=$(wc -c < "$LEGACY/$f")
      if (( size > 5242880 )); then printf '%10d %s\n' "$size" "$f"; fi
    fi
  done | sort -nr | head -100
  echo '```'
  echo
  echo "## Dependency / execution / security filenames (not file contents)"
  echo '```text'
  git -C "$LEGACY" ls-files 2>/dev/null | grep -Ei '(^|/)(readme|license|copying|notice|requirements[^/]*|pyproject.toml|poetry.lock|uv.lock|Pipfile|package.json|package-lock.json|yarn.lock|pnpm-lock.yaml|environment.yml|conda.yml|dockerfile|compose[^/]*\.ya?ml|makefile|tox.ini|pytest.ini|mypy.ini|\.github/workflows/|\.env(\..*)?$|\.gitignore|.*test.*|.*spec.*)' | head -500 || true
  echo '```text'
  echo
  echo "## Safety note"
  echo "This script did not run notebooks, install packages, inspect file contents, connect to the network, or print secret values. It cannot replace manual review. Inspect relevant files safely and document evidence in docs/legacy-audit/*."
} > "$REPORT"
chmod 600 "$REPORT" 2>/dev/null || true
printf 'Inventory written to: %s\n' "$REPORT"
