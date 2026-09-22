#!/usr/bin/env bash
# Backup the persistent data used by the lightweight, no-local-AI core stack.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${KAIRO_CORE_ENV_FILE:-${ROOT_DIR}/.env.core}"
PROJECT_NAME="${KAIRO_CORE_PROJECT_NAME:-kairo}"
TARGET_DIR="${1:-${ROOT_DIR}/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
WORK_DIR="${TARGET_DIR}/kairo-core-${STAMP}"

if [ ! -f "${ENV_FILE}" ]; then
    echo "Kairo core environment file not found: ${ENV_FILE}" >&2
    exit 1
fi

mkdir -p "${WORK_DIR}"
compose() {
    CORE_ENV_FILE="${ENV_FILE}" docker compose --project-name "${PROJECT_NAME}" --env-file "${ENV_FILE}" \
        -f "${ROOT_DIR}/docker-compose.core.yml" "$@"
}

env_value() {
    awk -v key="$1" 'index($0, key "=") == 1 { print substr($0, length(key) + 2); exit }' "${ENV_FILE}"
}

POSTGRES_USER="$(env_value POSTGRES_USER)"
POSTGRES_DB="$(env_value POSTGRES_DB)"
if [ -z "${POSTGRES_USER}" ] || [ -z "${POSTGRES_DB}" ]; then
    echo "POSTGRES_USER and POSTGRES_DB are required in ${ENV_FILE}" >&2
    exit 1
fi

compose exec -T postgres pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" > "${WORK_DIR}/postgres.sql"

redis_container="$(compose ps -q redis)"
minio_container="$(compose ps -q minio)"
docker cp "${redis_container}:/data/dump.rdb" "${WORK_DIR}/redis.rdb" 2>/dev/null || true
docker cp "${minio_container}:/data" "${WORK_DIR}/minio_data"

tar -C "${TARGET_DIR}" -czf "${WORK_DIR}.tar.gz" "$(basename "${WORK_DIR}")"
rm -rf "${WORK_DIR}"
echo "${WORK_DIR}.tar.gz"
