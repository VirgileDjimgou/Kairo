#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
# Kairo — Local Restore Script
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/kairo_ops.sh"

require_commands docker tar find mktemp
load_env_file

RESTORE_ARCHIVE="${1:-}"

if [ -z "${RESTORE_ARCHIVE}" ]; then
    echo "Usage: $0 /path/to/kairo-backup-YYYYMMDD_HHMMSS.tar.gz"
    exit 1
fi

if [ ! -f "${RESTORE_ARCHIVE}" ]; then
    echo "Error: backup archive not found: ${RESTORE_ARCHIVE}"
    exit 1
fi

echo "--- Kairo Restore ---"
echo "Archive: ${RESTORE_ARCHIVE}"
echo "Project: ${COMPOSE_PROJECT}"
echo "Mode:    ${KAIRO_DEPLOY_MODE}"
echo ""

echo "Starting restore dependencies..."
compose_cmd up -d postgres redis qdrant minio ollama
echo ""

# Extract to a temp directory
RESTORE_DIR="$(mktemp -d)"
echo "Extracting to ${RESTORE_DIR}..."
tar -xzf "${RESTORE_ARCHIVE}" -C "${RESTORE_DIR}"

# Find the backup directory (may have a single top-level dir)
BACKUP_CONTENT_DIR="${RESTORE_DIR}"
SUB_DIR="$(find "${RESTORE_DIR}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | head -1)"
if [ -n "${SUB_DIR}" ]; then
    BACKUP_CONTENT_DIR="${SUB_DIR}"
fi

echo "Backup content directory: ${BACKUP_CONTENT_DIR}"
echo ""

# 1. PostgreSQL
POSTGRES_DUMP="${BACKUP_CONTENT_DIR}/postgres.sql"
if [ -f "${POSTGRES_DUMP}" ]; then
    echo "[1/5] Restoring PostgreSQL database..."
    compose_cmd exec -T postgres \
        psql -U "${POSTGRES_USER:-orgmind}" -d "${POSTGRES_DB:-orgmind}" \
        < "${POSTGRES_DUMP}"
    echo "      -> PostgreSQL restore complete"
else
    echo "[1/5] Skipping PostgreSQL — no dump found"
fi

# 2. Redis
REDIS_RDB="${BACKUP_CONTENT_DIR}/redis.rdb"
if [ -f "${REDIS_RDB}" ]; then
    echo "[2/5] Restoring Redis RDB..."
    REDIS_CONTAINER=$(compose_cmd ps -q redis 2>/dev/null)
    if [ -n "${REDIS_CONTAINER}" ]; then
        docker cp "${REDIS_RDB}" "${REDIS_CONTAINER}:/data/dump.rdb"
        # Restart redis to reload the RDB
        compose_cmd restart redis
        echo "      -> Redis RDB restored and container restarted"
    else
        echo "      -> (Redis container not running — skipped)"
    fi
else
    echo "[2/5] Skipping Redis — no RDB snapshot found"
fi

# 3. Qdrant
QDRANT_STORAGE="${BACKUP_CONTENT_DIR}/qdrant_storage"
if [ -d "${QDRANT_STORAGE}" ]; then
    echo "[3/5] Restoring Qdrant storage..."
    QDRANT_CONTAINER=$(compose_cmd ps -q qdrant 2>/dev/null)
    if [ -n "${QDRANT_CONTAINER}" ]; then
        compose_cmd stop qdrant
        docker cp "${QDRANT_STORAGE}" "${QDRANT_CONTAINER}:/qdrant/storage"
        compose_cmd start qdrant
        echo "      -> Qdrant storage restored and container restarted"
    else
        echo "      -> (Qdrant container not running — skipped)"
    fi
else
    echo "[3/5] Skipping Qdrant — no storage directory found"
fi

# 4. MinIO
MINIO_DATA="${BACKUP_CONTENT_DIR}/minio_data"
if [ -d "${MINIO_DATA}" ]; then
    echo "[4/5] Restoring MinIO data..."
    MINIO_CONTAINER=$(compose_cmd ps -q minio 2>/dev/null)
    if [ -n "${MINIO_CONTAINER}" ]; then
        compose_cmd stop minio
        docker cp "${MINIO_DATA}" "${MINIO_CONTAINER}:/data"
        compose_cmd start minio
        echo "      -> MinIO data restored and container restarted"
    else
        echo "      -> (MinIO container not running — skipped)"
    fi
else
    echo "[4/5] Skipping MinIO — no data directory found"
fi

# 5. Ollama
OLLAMA_DATA="${BACKUP_CONTENT_DIR}/ollama_data"
if [ -d "${OLLAMA_DATA}" ]; then
    echo "[5/5] Restoring Ollama models..."
    OLLAMA_CONTAINER=$(compose_cmd ps -q ollama 2>/dev/null)
    if [ -n "${OLLAMA_CONTAINER}" ]; then
        compose_cmd stop ollama
        docker cp "${OLLAMA_DATA}" "${OLLAMA_CONTAINER}:/root/.ollama"
        compose_cmd start ollama
        echo "      -> Ollama models restored and container restarted"
    else
        echo "      -> (Ollama container not running — skipped)"
    fi
else
    echo "[5/5] Skipping Ollama — no model data found"
fi

# Clean up
echo ""
echo "Cleaning up..."
rm -rf "${RESTORE_DIR}"

echo "Starting application services..."
compose_cmd up -d api worker web

echo ""
echo "--- Restore complete ---"
echo ""
echo "Services that were restarted may take a moment to become healthy."
echo "Run 'docker compose ps' to verify all services are up."
echo "Run 'scripts/production_smoke.sh' to verify basic functionality."
echo ""
