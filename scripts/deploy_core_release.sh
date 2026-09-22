#!/usr/bin/env bash
# Deploy the isolated Web/PWA core stack. It intentionally never targets the
# default Compose project and therefore cannot stop an unrelated application.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${KAIRO_CORE_ENV_FILE:-${ROOT_DIR}/.env.core}"
PROJECT_NAME="${KAIRO_CORE_PROJECT_NAME:-kairo}"
MODE="${1:-preflight}"

if [ ! -f "${ENV_FILE}" ]; then
    echo "Kairo core environment file not found: ${ENV_FILE}" >&2
    exit 1
fi

env_value() {
    awk -v key="$1" 'index($0, key "=") == 1 { print substr($0, length(key) + 2); exit }' "${ENV_FILE}"
}

APP_ENV="$(env_value APP_ENV)"
APP_DEBUG="$(env_value APP_DEBUG)"
APP_BASE_URL="$(env_value APP_BASE_URL)"
CORS_ORIGINS="$(env_value CORS_ORIGINS)"
JWT_SECRET_KEY="$(env_value JWT_SECRET_KEY)"
POSTGRES_PASSWORD="$(env_value POSTGRES_PASSWORD)"
MINIO_ROOT_PASSWORD="$(env_value MINIO_ROOT_PASSWORD)"
CLOUDFLARE_TUNNEL_TOKEN="$(env_value CLOUDFLARE_TUNNEL_TOKEN)"
BACKUP_ENCRYPTION_KEY="$(env_value BACKUP_ENCRYPTION_KEY)"
BACKUP_MANIFEST_SIGNING_KEY="$(env_value BACKUP_MANIFEST_SIGNING_KEY)"

compose() {
    CORE_ENV_FILE="${ENV_FILE}" docker compose --project-name "${PROJECT_NAME}" --env-file "${ENV_FILE}" \
        -f "${ROOT_DIR}/docker-compose.core.yml" "$@"
}

require_value() {
    local name="$1"
    local value
    value="$(env_value "${name}")"
    if [ -z "${value}" ] || [[ "${value}" == replace-with-* ]]; then
        echo "Production value required: ${name}" >&2
        exit 1
    fi
}

preflight() {
    [ "${APP_ENV}" = "production" ] || { echo "APP_ENV must be production" >&2; exit 1; }
    [ "${APP_DEBUG}" = "false" ] || { echo "APP_DEBUG must be false" >&2; exit 1; }
    for name in APP_BASE_URL CORS_ORIGINS JWT_SECRET_KEY POSTGRES_PASSWORD MINIO_ROOT_PASSWORD \
        CLOUDFLARE_TUNNEL_TOKEN BACKUP_ENCRYPTION_KEY BACKUP_MANIFEST_SIGNING_KEY; do
        require_value "${name}"
    done
    compose config --quiet
}

deploy() {
    compose build
    compose up -d postgres redis minio
    compose run --rm api alembic upgrade head
    compose up -d api worker scheduler web
    compose --profile tunnel up -d cloudflared
    KAIRO_ENV_FILE="${ENV_FILE}" "${ROOT_DIR}/scripts/production_smoke.sh" "${APP_BASE_URL}"
}

case "${MODE}" in
    preflight)
        preflight
        ;;
    install)
        preflight
        deploy
        ;;
    upgrade)
        preflight
        "${ROOT_DIR}/scripts/backup_core.sh"
        deploy
        ;;
    *)
        echo "Usage: $0 [preflight|install|upgrade]" >&2
        exit 2
        ;;
esac
