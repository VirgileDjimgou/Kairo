#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
# Kairo — Release Rollback Helper
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/kairo_ops.sh"

require_commands bash docker

RESTORE_ARCHIVE="${1:-}"
SMOKE_URL="${KAIRO_SMOKE_URL:-}"

if [ -z "${RESTORE_ARCHIVE}" ]; then
    echo "Usage: $0 /path/to/kairo-backup-YYYYMMDD_HHMMSS.tar.gz" >&2
    exit 1
fi

kairo_log "Running rollback preflight..."
preflight_env_checks
compose_config_check
print_runtime_summary

kairo_log "Restoring from ${RESTORE_ARCHIVE}..."
bash "${SCRIPT_DIR}/restore.sh" "${RESTORE_ARCHIVE}"

kairo_log "Running post-rollback smoke check..."
if [ -n "${SMOKE_URL}" ]; then
    bash "${SCRIPT_DIR}/production_smoke.sh" "${SMOKE_URL}"
else
    bash "${SCRIPT_DIR}/production_smoke.sh"
fi

kairo_log "Rollback workflow completed."
