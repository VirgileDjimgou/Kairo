#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
# Kairo — Production Smoke Check
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/kairo_ops.sh"

require_commands curl grep
load_env_file

BASE_URL="${1:-${APP_BASE_URL:-http://localhost}}"
PASS=0
FAIL=0

check() {
    local label="$1"
    local url="$2"
    local expect_status="${3:-200}"
    local expect_body="${4:-}"

    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" "${url}" 2>/dev/null || echo "000")

    if [ "${status}" != "${expect_status}" ]; then
        echo "  FAIL  ${label} — expected HTTP ${expect_status}, got ${status}"
        FAIL=$((FAIL + 1))
        return 1
    fi

    if [ -n "${expect_body}" ]; then
        local body
        body=$(curl -fsS "${url}" 2>/dev/null || echo "")
        if ! echo "${body}" | grep -q "${expect_body}"; then
            echo "  FAIL  ${label} — body missing '${expect_body}'"
            FAIL=$((FAIL + 1))
            return 1
        fi
    fi

    echo "  PASS  ${label}"
    PASS=$((PASS + 1))
}

echo "--- Kairo Production Smoke Check ---"
echo "Target: ${BASE_URL}"
echo ""

check "Health endpoint"               "${BASE_URL}/health"              200 "\"status\""
check "Metrics endpoint"              "${BASE_URL}/metrics"             200 "# HELP"
check "Root page"                     "${BASE_URL}/"                    200
check "API docs blocked"              "${BASE_URL}/docs"                404
check "API redoc blocked"             "${BASE_URL}/redoc"               404
check "OpenAPI blocked"               "${BASE_URL}/openapi.json"        404

echo ""
echo "--- Results: ${PASS} passed, ${FAIL} failed ---"

if [ "${FAIL}" -gt 0 ]; then
    exit 1
fi
