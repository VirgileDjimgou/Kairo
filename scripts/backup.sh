#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
# Kairo — Local Backup Script
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/kairo_ops.sh"

require_commands docker tar wc du
load_env_file

BACKUP_DIR="${1:-${KAIRO_REPO_ROOT}/backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="${BACKUP_DIR}/kairo-backup-${TIMESTAMP}"

mkdir -p "${BACKUP_PATH}"

echo "--- Kairo Backup ---"
echo "Target:  ${BACKUP_PATH}"
echo "Project: ${COMPOSE_PROJECT}"
echo "Mode:    ${KAIRO_DEPLOY_MODE}"
echo ""

# 1. PostgreSQL
echo "[1/5] Dumping PostgreSQL database..."
compose_cmd exec -T postgres pg_dumpall \
    -U "${POSTGRES_USER:-orgmind}" \
    > "${BACKUP_PATH}/postgres.sql"
echo "      -> postgres.sql ($(wc -c < "${BACKUP_PATH}/postgres.sql") bytes)"

# 2. Redis
echo "[2/5] Copying Redis RDB..."
REDIS_CONTAINER=$(compose_cmd ps -q redis 2>/dev/null)
if [ -n "${REDIS_CONTAINER}" ]; then
    docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${BACKUP_PATH}/redis.rdb" 2>/dev/null || \
        echo "      -> (no RDB snapshot found — Redis may be empty)"
else
    echo "      -> (Redis container not running — skipped)"
fi

# 3. Qdrant
echo "[3/5] Copying Qdrant storage..."
QDRANT_CONTAINER=$(compose_cmd ps -q qdrant 2>/dev/null)
if [ -n "${QDRANT_CONTAINER}" ]; then
    docker cp "${QDRANT_CONTAINER}:/qdrant/storage" "${BACKUP_PATH}/qdrant_storage" 2>/dev/null
    echo "      -> qdrant_storage/ backed up"
else
    echo "      -> (Qdrant container not running — skipped)"
fi

# 4. MinIO
echo "[4/5] Copying MinIO data..."
MINIO_CONTAINER=$(compose_cmd ps -q minio 2>/dev/null)
if [ -n "${MINIO_CONTAINER}" ]; then
    docker cp "${MINIO_CONTAINER}:/data" "${BACKUP_PATH}/minio_data" 2>/dev/null
    echo "      -> minio_data/ backed up"
else
    echo "      -> (MinIO container not running — skipped)"
fi

# 5. Ollama
echo "[5/5] Copying Ollama models..."
OLLAMA_CONTAINER=$(compose_cmd ps -q ollama 2>/dev/null)
if [ -n "${OLLAMA_CONTAINER}" ]; then
    docker cp "${OLLAMA_CONTAINER}:/root/.ollama" "${BACKUP_PATH}/ollama_data" 2>/dev/null
    echo "      -> ollama_data/ backed up"
else
    echo "      -> (Ollama container not running — skipped)"
fi

# Compress
echo ""
echo "Compressing backup..."
tar -czf "${BACKUP_PATH}.tar.gz" -C "${BACKUP_DIR}" "kairo-backup-${TIMESTAMP}"
rm -rf "${BACKUP_PATH}"

echo ""
echo "--- Backup complete ---"
echo "Archive: ${BACKUP_PATH}.tar.gz"
echo "Size:    $(du -h "${BACKUP_PATH}.tar.gz" | cut -f1)"
echo ""
echo "To restore, see: docs/deployment-guide.md"
