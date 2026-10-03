from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime, timedelta

import httpx
import structlog
from qdrant_client import AsyncQdrantClient
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = structlog.get_logger(__name__)


async def _check_db(db: AsyncSession) -> dict:
    start = time.monotonic()
    try:
        await db.execute(sa_text("SELECT 1"))
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("DB health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_redis() -> dict:
    start = time.monotonic()
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(
            settings.redis_url,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        await r.ping()
        await r.aclose()
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("Redis health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_minio() -> dict:
    def _sync_check() -> dict:
        import boto3
        from botocore.client import Config

        client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_root_user,
            aws_secret_access_key=settings.minio_root_password,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                connect_timeout=3,
                read_timeout=3,
            ),
        )
        client.list_buckets()
        return {}

    start = time.monotonic()
    try:
        await asyncio.wait_for(asyncio.to_thread(_sync_check), timeout=5)
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except (TimeoutError, Exception) as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("MinIO health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_qdrant() -> dict:
    if not settings.ai_runtime_enabled:
        return {"status": "disabled", "latency_ms": 0}
    if settings.ai_runtime_mode == "remote":
        return await _check_remote_ai_runtime()
    start = time.monotonic()
    try:
        client = AsyncQdrantClient(url=settings.qdrant_url, timeout=5)
        await client.get_collections()
        await client.close()
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("Qdrant health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_llm_provider() -> dict:
    if not settings.ai_runtime_enabled:
        return {"status": "disabled", "latency_ms": 0}
    if settings.llm_provider_kind == "remote_ai_runtime":
        return await _check_remote_ai_runtime()
    start = time.monotonic()
    try:
        if settings.llm_provider_kind == "openai_compatible":
            async with httpx.AsyncClient(
                base_url=settings.openai_compatible_base_url,
                timeout=5,
            ) as c:
                resp = await c.get("/models")
        else:
            async with httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=5) as c:
                resp = await c.get("/api/tags")
            resp.raise_for_status()
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("LLM provider health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_embedding_provider() -> dict:
    if not settings.ai_runtime_enabled:
        return {"status": "disabled", "latency_ms": 0}
    if settings.embedding_provider_kind == "remote_ai_runtime":
        return await _check_remote_ai_runtime()
    start = time.monotonic()
    try:
        if settings.embedding_provider_kind == "openai_compatible":
            async with httpx.AsyncClient(
                base_url=settings.openai_compatible_base_url,
                timeout=5,
            ) as c:
                resp = await c.get("/models")
        else:
            async with httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=5) as c:
                resp = await c.get("/api/tags")
        resp.raise_for_status()
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("Embedding provider health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_remote_ai_runtime() -> dict:
    from app.providers.ai_runtime.remote import _RemoteAiRuntimeClient

    start = time.monotonic()
    try:
        client = _RemoteAiRuntimeClient()
        await client.request("GET", "/health")
        return {"status": "ok", "latency_ms": int((time.monotonic() - start) * 1000)}
    except Exception as exc:
        return {
            "status": "unavailable",
            "latency_ms": int((time.monotonic() - start) * 1000),
            "detail": str(exc),
        }


OUTBOX_BACKLOG_DEGRADED_SECONDS = 300
BACKUP_STALE_AFTER_DAYS = 7
BACKUP_STALE_AFTER_SECONDS = BACKUP_STALE_AFTER_DAYS * 86400


def _outbox_status(
    *, pending: int, failed: int, oldest_pending_seconds: int | None
) -> str:
    if failed > 0:
        return "degraded"
    if oldest_pending_seconds is not None and oldest_pending_seconds > OUTBOX_BACKLOG_DEGRADED_SECONDS:
        return "degraded"
    return "ok"


async def _check_notification_outbox(db: AsyncSession) -> dict:
    from sqlalchemy import func, select

    from app.modules.notifications.user_models import NotificationOutboxEvent

    start = time.monotonic()
    try:
        pending = int(
            await db.scalar(
                select(func.count(NotificationOutboxEvent.id)).where(
                    NotificationOutboxEvent.status == "pending"
                )
            )
            or 0
        )
        failed = int(
            await db.scalar(
                select(func.count(NotificationOutboxEvent.id)).where(
                    NotificationOutboxEvent.status == "failed"
                )
            )
            or 0
        )
        oldest = await db.scalar(
            select(func.min(NotificationOutboxEvent.created_at)).where(
                NotificationOutboxEvent.status == "pending"
            )
        )
        if oldest is not None and oldest.tzinfo is None:
            oldest = oldest.replace(tzinfo=UTC)
        oldest_seconds = (
            int((datetime.now(UTC) - oldest).total_seconds()) if oldest is not None else None
        )
        lease_cutoff = datetime.now(UTC) - timedelta(
            seconds=max(1, settings.outbox_processing_lease_seconds)
        )
        stranded = int(
            await db.scalar(
                select(func.count(NotificationOutboxEvent.id)).where(
                    NotificationOutboxEvent.status == "processing",
                    NotificationOutboxEvent.processing_started_at.is_not(None),
                    NotificationOutboxEvent.processing_started_at < lease_cutoff,
                )
            )
            or 0
        )
        retrying = int(
            await db.scalar(
                select(func.count(NotificationOutboxEvent.id)).where(
                    NotificationOutboxEvent.status == "pending",
                    NotificationOutboxEvent.attempts > 0,
                )
            )
            or 0
        )
        elapsed = int((time.monotonic() - start) * 1000)
        return {
            "status": _outbox_status(
                pending=pending, failed=failed, oldest_pending_seconds=oldest_seconds
            ),
            "latency_ms": elapsed,
            "detail": {
                "pending": pending,
                "failed": failed,
                "oldest_pending_seconds": oldest_seconds,
                "stranded": stranded,
                "retrying": retrying,
            },
        }
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("Notification outbox health probe failed", error=str(exc))
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_domain_event_outbox(db: AsyncSession) -> dict:
    from sqlalchemy import func, select

    from app.modules.domain_events.models import DomainEvent

    start = time.monotonic()
    try:
        pending = int(
            await db.scalar(
                select(func.count(DomainEvent.id)).where(DomainEvent.status == "pending")
            )
            or 0
        )
        failed = int(
            await db.scalar(
                select(func.count(DomainEvent.id)).where(DomainEvent.status == "failed")
            )
            or 0
        )
        oldest = await db.scalar(
            select(func.min(DomainEvent.created_at)).where(DomainEvent.status == "pending")
        )
        if oldest is not None and oldest.tzinfo is None:
            oldest = oldest.replace(tzinfo=UTC)
        oldest_seconds = (
            int((datetime.now(UTC) - oldest).total_seconds()) if oldest is not None else None
        )
        elapsed = int((time.monotonic() - start) * 1000)
        return {
            "status": _outbox_status(
                pending=pending, failed=failed, oldest_pending_seconds=oldest_seconds
            ),
            "latency_ms": elapsed,
            "detail": {
                "pending": pending,
                "failed": failed,
                "oldest_pending_seconds": oldest_seconds,
            },
        }
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("Domain event outbox health probe failed", error=str(exc))
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_backup(db: AsyncSession) -> dict:
    if not settings.backup_enabled:
        return {"status": "disabled", "latency_ms": 0}

    from sqlalchemy import func, select

    from app.modules.backup.models import BackupRun

    start = time.monotonic()
    try:
        last_success_at = await db.scalar(
            select(func.max(BackupRun.completed_at)).where(
                BackupRun.status.in_(("available", "restore_drill_passed"))
            )
        )
        if last_success_at is not None and last_success_at.tzinfo is None:
            last_success_at = last_success_at.replace(tzinfo=UTC)
        age_seconds = (
            int((datetime.now(UTC) - last_success_at).total_seconds())
            if last_success_at is not None
            else None
        )
        elapsed = int((time.monotonic() - start) * 1000)
        if age_seconds is None:
            status = "degraded"
        elif age_seconds > BACKUP_STALE_AFTER_SECONDS:
            status = "degraded"
        else:
            status = "ok"
        return {
            "status": status,
            "latency_ms": elapsed,
            "detail": {"last_successful_backup_seconds": age_seconds},
        }
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("Backup health probe failed", error=str(exc))
        return {"status": "unavailable", "latency_ms": elapsed}


async def run_all_checks(db: AsyncSession) -> dict[str, object]:
    # Database-backed probes share one AsyncSession and therefore run
    # sequentially; only the independent external probes are gathered.
    db_checks = {
        "database": _check_db(db),
        "backup": _check_backup(db),
        "notification_outbox": _check_notification_outbox(db),
        "domain_event_outbox": _check_domain_event_outbox(db),
    }
    try:
        from app.modules.module_registry.descriptor import registered_health_checks

        for module_key, check in registered_health_checks().items():
            db_checks[module_key] = check(db)
    except Exception as exc:  # a broken optional hook must not hide core health
        logger.error("Module health check discovery failed", error=str(exc))
    external_checks = {
        "redis": _check_redis(),
        "minio": _check_minio(),
        "qdrant": _check_qdrant(),
        "llm_provider": _check_llm_provider(),
        "embedding_provider": _check_embedding_provider(),
    }
    output: dict[str, object] = {}
    for name, coroutine in db_checks.items():
        try:
            output[name] = await coroutine
        except Exception as exc:  # pragma: no cover - defensive mirror of gather path
            logger.error("Unexpected health check error", service=name, error=str(exc))
            output[name] = {"status": "error", "latency_ms": -1, "detail": str(exc)}

    results = await asyncio.gather(*external_checks.values(), return_exceptions=True)
    for name, result in zip(external_checks, results, strict=False):
        if isinstance(result, Exception):
            logger.error("Unexpected health check error", service=name, error=str(result))
            output[name] = {"status": "error", "latency_ms": -1, "detail": str(result)}
        else:
            output[name] = result
    return output


async def run_readiness_checks(db: AsyncSession) -> dict[str, object]:
    """Critical dependencies only: traffic can be served when these are ok."""
    checks = {
        "database": _check_db(db),
        "redis": _check_redis(),
    }
    output: dict[str, object] = {}
    for name, coroutine in checks.items():
        try:
            output[name] = await coroutine
        except Exception as exc:  # pragma: no cover - defensive
            output[name] = {"status": "error", "latency_ms": -1, "detail": str(exc)}
    return output
