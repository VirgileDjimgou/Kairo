#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
# Kairo — Local Backup Script
# ───────────────────────────────────────────────────────────────────────────────
# Creates timestamped backups of all persistent Docker volumes.
#
# Usage:
#   chmod +x scripts/backup.sh
#   ./scripts/backup.sh                    # backup to ./backups/
#   ./scripts/backup.sh /path/to/dir       # backup to custom directory
#
# What gets backed up:
#   - PostgreSQL database (SQL dump)
#   - Redis data (RDB snapshot)
#   - Qdrant vector store
#   - MinIO object storage
#   - Ollama model data
#
# Restore:
#   See "Restoring from a backup" in docs/deployment-guide.md
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

BACKUP_DIR="${1:-./backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="${BACKUP_DIR}/kairo-backup-${TIMESTAMP}"
COMPOSE_PROJECT="${COMPOSE_PROJECT:-kairo}"

mkdir -p "${BACKUP_PATH}"

echo "--- Kairo Backup ---"
echo "Target:  ${BACKUP_PATH}"
echo "Project: ${COMPOSE_PROJECT}"
echo ""

# 1. PostgreSQL
echo "[1/5] Dumping PostgreSQL database..."
docker compose -p "${COMPOSE_PROJECT}" exec -T postgres pg_dumpall \
    -U "${POSTGRES_USER:-orgmind}" \
    > "${BACKUP_PATH}/postgres.sql"
echo "      -> postgres.sql ($(wc -c < "${BACKUP_PATH}/postgres.sql") bytes)"

# 2. Redis
echo "[2/5] Copying Redis RDB..."
REDIS_CONTAINER=$(docker compose -p "${COMPOSE_PROJECT}" ps -q redis 2>/dev/null)
if [ -n "${REDIS_CONTAINER}" ]; then
    docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${BACKUP_PATH}/redis.rdb" 2>/dev/null || \
        echo "      -> (no RDB snapshot found — Redis may be empty)"
else
    echo "      -> (Redis container not running — skipped)"
fi

# 3. Qdrant
echo "[3/5] Copying Qdrant storage..."
QDRANT_CONTAINER=$(docker compose -p "${COMPOSE_PROJECT}" ps -q qdrant 2>/dev/null)
if [ -n "${QDRANT_CONTAINER}" ]; then
    docker cp "${QDRANT_CONTAINER}:/qdrant/storage" "${BACKUP_PATH}/qdrant_storage" 2>/dev/null
    echo "      -> qdrant_storage/ backed up"
else
    echo "      -> (Qdrant container not running — skipped)"
fi

# 4. MinIO
echo "[4/5] Copying MinIO data..."
MINIO_CONTAINER=$(docker compose -p "${COMPOSE_PROJECT}" ps -q minio 2>/dev/null)
if [ -n "${MINIO_CONTAINER}" ]; then
    docker cp "${MINIO_CONTAINER}:/data" "${BACKUP_PATH}/minio_data" 2>/dev/null
    echo "      -> minio_data/ backed up"
else
    echo "      -> (MinIO container not running — skipped)"
fi

# 5. Ollama
echo "[5/5] Copying Ollama models..."
OLLAMA_CONTAINER=$(docker compose -p "${COMPOSE_PROJECT}" ps -q ollama 2>/dev/null)
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

