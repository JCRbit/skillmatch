#!/usr/bin/env bash
# Smoke test for the API production image (task P-06).
#
# Usage: scripts/smoke_test_image.sh IMAGE [EXPECTED_REVISION]
#
#   IMAGE              Image to test, e.g. skillmatch-api:local (must already exist locally).
#   EXPECTED_REVISION  Optional commit SHA the image must be labelled with.
#
# Used by CI (job "Infra") and by the publish workflow, so a pull request and a release run the
# same checks. Needs Docker and curl. It starts one throwaway container without a database:
# GET /health is a liveness probe and must not depend on one.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 IMAGE [EXPECTED_REVISION]" >&2
  exit 2
fi

image="$1"
expected_revision="${2:-}"
container=""
failures=0

pass() { echo "  ok   $*"; }
fail() { echo "  FAIL $*" >&2; failures=$((failures + 1)); }

cleanup() {
  if [[ -n "${container}" ]]; then
    if ((failures > 0)); then
      echo "--- container logs ---" >&2
      docker logs "${container}" >&2 || true
    fi
    docker rm --force "${container}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "Smoke test: ${image}"

# 1) The image runs as an unprivileged user.
uid="$(docker run --rm --entrypoint id "${image}" -u)"
if [[ "${uid}" != "0" ]]; then pass "runs as uid ${uid} (not root)"; else fail "runs as root"; fi

# 2) Traceability: the revision label matches the commit the image was built from.
revision="$(docker image inspect --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' "${image}")"
if [[ -z "${revision}" || "${revision}" == "unknown" ]]; then
  fail "label org.opencontainers.image.revision is missing (build with --build-arg GIT_SHA=...)"
elif [[ -n "${expected_revision}" && "${revision}" != "${expected_revision}" ]]; then
  fail "revision label is ${revision}, expected ${expected_revision}"
else
  pass "revision label ${revision}"
fi

# 3) No development tooling, no uv and no test suite in the image.
if docker run --rm --entrypoint python "${image}" -c \
  "import importlib.util as u, sys; sys.exit(any(u.find_spec(m) for m in ('pytest', 'mypy')))"; then
  pass "no dev dependencies (pytest, mypy)"
else
  fail "dev dependencies are installed"
fi
if docker run --rm --entrypoint sh "${image}" -c 'command -v uv >/dev/null 2>&1 || test -e /app/tests'; then
  fail "uv or /app/tests is present in the image"
else
  pass "no uv and no tests in the image"
fi

# 4) Migrations tooling and scripts are present, so `alembic upgrade head` can run from this image.
if heads="$(docker run --rm --entrypoint alembic "${image}" heads 2>&1)" && [[ -n "${heads}" ]]; then
  pass "alembic sees the migrations (${heads%%$'\n'*})"
else
  fail "alembic cannot read the migrations: ${heads:-no output}"
fi

# 5) The application starts and answers its health check.
container="$(docker run --detach --publish 127.0.0.1::8000 \
  --cap-drop ALL --security-opt no-new-privileges:true "${image}")"
address="$(docker port "${container}" 8000/tcp)"
address="${address%%$'\n'*}"
base_url="http://${address}"

healthy=0
for _ in $(seq 1 30); do
  if body="$(curl --fail --silent --show-error --max-time 2 "${base_url}/health" 2>/dev/null)"; then
    healthy=1
    break
  fi
  sleep 1
done
if ((healthy == 1)) && [[ "${body}" == *'"status":"ok"'* ]]; then
  pass "GET /health -> ${body}"
else
  fail "GET /health did not return status ok within 30 s"
fi

# 6) Production defaults: interactive docs and the OpenAPI schema are not exposed.
for path in /docs /openapi.json; do
  code="$(curl --silent --output /dev/null --write-out '%{http_code}' --max-time 2 "${base_url}${path}" || true)"
  if [[ "${code}" == "404" ]]; then pass "GET ${path} -> 404"; else fail "GET ${path} -> ${code}, expected 404"; fi
done

if ((failures > 0)); then
  echo "Smoke test FAILED (${failures} check(s))." >&2
  exit 1
fi
echo "Smoke test passed."
