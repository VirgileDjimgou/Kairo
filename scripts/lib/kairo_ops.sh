#!/usr/bin/env bash

set -euo pipefail

KAIRO_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KAIRO_REPO_ROOT="$(cd "${KAIRO_LIB_DIR}/../.." && pwd)"
KAIRO_ENV_FILE="${KAIRO_ENV_FILE:-${KAIRO_REPO_ROOT}/.env}"
KAIRO_DEPLOY_MODE="${KAIRO_DEPLOY_MODE:-production}"
COMPOSE_PROJECT="${COMPOSE_PROJECT:-kairo}"
export KAIRO_ENV_FILE
export KAIRO_DEPLOY_MODE
export COMPOSE_PROJECT

kairo_log() {
    echo "[kairo-ops] $*"
}

kairo_fail() {
    echo "[kairo-ops] ERROR: $*" >&2
    exit 1
}

require_commands() {
    local missing=0
    local command_name
    for command_name in "$@"; do
        if ! command -v "${command_name}" >/dev/null 2>&1; then
            echo "[kairo-ops] Missing required command: ${command_name}" >&2
            missing=1
        fi
    done

    if [ "${missing}" -ne 0 ]; then
        exit 1
    fi
}

ensure_env_file() {
    if [ ! -f "${KAIRO_ENV_FILE}" ]; then
        kairo_fail "Environment file not found: ${KAIRO_ENV_FILE}"
    fi
}

load_env_file() {
    ensure_env_file
    while IFS= read -r line || [ -n "${line}" ]; do
        line="${line%$'\r'}"
        case "${line}" in
            ""|\#*)
                continue
                ;;
        esac

        if [[ "${line}" != *=* ]]; then
            continue
        fi

        local key="${line%%=*}"
        local value="${line#*=}"
        key="${key#"${key%%[![:space:]]*}"}"
        key="${key%"${key##*[![:space:]]}"}"
        export "${key}=${value}"
    done < "${KAIRO_ENV_FILE}"
}

compose_args() {
    if [ "${KAIRO_DEPLOY_MODE}" = "production" ]; then
        printf '%s\n' \
            "-f" "${KAIRO_REPO_ROOT}/docker-compose.yml" \
            "-f" "${KAIRO_REPO_ROOT}/docker-compose.prod.yml"
    else
        printf '%s\n' "-f" "${KAIRO_REPO_ROOT}/docker-compose.yml"
    fi
}

compose_cmd() {
    local args=()
    while IFS= read -r line; do
        args+=("${line}")
    done < <(compose_args)

    docker compose "${args[@]}" --env-file "${KAIRO_ENV_FILE}" -p "${COMPOSE_PROJECT}" "$@"
}

is_placeholder_secret() {
    local value="${1:-}"
    case "${value}" in
        ""|change-me*|orgmind_dev_password)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

preflight_env_checks() {
    load_env_file

    local failures=0

    if [ "${APP_ENV:-}" != "production" ]; then
        echo "[kairo-ops] APP_ENV should be 'production' for the packaging flow." >&2
        failures=1
    fi

    if [ "${APP_DEBUG:-true}" != "false" ]; then
        echo "[kairo-ops] APP_DEBUG should be 'false' for the packaging flow." >&2
        failures=1
    fi

    if is_placeholder_secret "${JWT_SECRET_KEY:-}"; then
        echo "[kairo-ops] JWT_SECRET_KEY still looks like a placeholder." >&2
        failures=1
    fi

    if is_placeholder_secret "${POSTGRES_PASSWORD:-}"; then
        echo "[kairo-ops] POSTGRES_PASSWORD still looks like a placeholder." >&2
        failures=1
    fi

    if is_placeholder_secret "${MINIO_ROOT_PASSWORD:-}"; then
        echo "[kairo-ops] MINIO_ROOT_PASSWORD still looks like a placeholder." >&2
        failures=1
    fi

    if [ -z "${APP_BASE_URL:-}" ]; then
        echo "[kairo-ops] APP_BASE_URL must be set." >&2
        failures=1
    fi

    if [ -z "${CORS_ORIGINS:-}" ]; then
        echo "[kairo-ops] CORS_ORIGINS must be set." >&2
        failures=1
    fi

    if [ "${failures}" -ne 0 ]; then
        exit 1
    fi
}

compose_config_check() {
    compose_cmd config >/dev/null
}

print_runtime_summary() {
    load_env_file
    kairo_log "Deployment mode: ${KAIRO_DEPLOY_MODE}"
    kairo_log "Compose project: ${COMPOSE_PROJECT}"
    kairo_log "Environment file: ${KAIRO_ENV_FILE}"
    kairo_log "App base URL: ${APP_BASE_URL:-unset}"
}
