#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
# Kairo — Release Deployment Helper
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/kairo_ops.sh"

require_commands docker bash

MODE="${1:-preflight}"
SKIP_BACKUP="${KAIRO_SKIP_BACKUP:-0}"
RUN_SEED="${KAIRO_RUN_DEMO_SEED:-0}"
SMOKE_URL="${KAIRO_SMOKE_URL:-}"

run_preflight() {
    kairo_log "Running environment and compose preflight checks..."
    preflight_env_checks
    compose_config_check
    print_runtime_summary
    kairo_log "Preflight checks passed."
}

run_stack_update() {
    if [ "${MODE}" = "upgrade" ] && [ "${SKIP_BACKUP}" != "1" ]; then
        kairo_log "Creating a safety backup before upgrade..."
        bash "${SCRIPT_DIR}/backup.sh"
    fi

    kairo_log "Building production images..."
    compose_cmd build api web worker

    kairo_log "Starting production stack..."
    compose_cmd up -d postgres redis qdrant minio ollama api worker web

    kairo_log "Applying database migrations..."
    compose_cmd exec -T api alembic upgrade head

    if [ "${RUN_SEED}" = "1" ]; then
        kairo_log "Running demo seed on the target stack..."
        compose_cmd exec -T api python -m app.db.seed
    fi

    kairo_log "Running production smoke check..."
    if [ -n "${SMOKE_URL}" ]; then
        bash "${SCRIPT_DIR}/production_smoke.sh" "${SMOKE_URL}"
    else
        bash "${SCRIPT_DIR}/production_smoke.sh"
    fi
}

case "${MODE}" in
    preflight)
        run_preflight
        ;;
    install)
        run_preflight
        run_stack_update
        ;;
    upgrade)
        run_preflight
        run_stack_update
        ;;
    *)
        echo "Usage: $0 [preflight|install|upgrade]" >&2
        echo "Environment toggles:" >&2
        echo "  KAIRO_SKIP_BACKUP=1      Skip the automatic backup during upgrade" >&2
        echo "  KAIRO_RUN_DEMO_SEED=1    Run the demo seed after install/upgrade" >&2
        echo "  KAIRO_SMOKE_URL=https://example.com  Override the smoke-check URL" >&2
        exit 1
        ;;
esac
