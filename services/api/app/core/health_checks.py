from __future__ import annotations

import asyncio
import time

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
        await asyncio.wait_for(
            asyncio.to_thread(_sync_check), timeout=5
        )
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except (TimeoutError, Exception) as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("MinIO health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def _check_qdrant() -> dict:
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


async def _check_ollama() -> dict:
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(
            base_url=settings.ollama_base_url, timeout=5
        ) as c:
            resp = await c.get("/api/tags")
            resp.raise_for_status()
        elapsed = int((time.monotonic() - start) * 1000)
        return {"status": "ok", "latency_ms": elapsed}
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.warning("Ollama health probe failed", error=str(exc), latency_ms=elapsed)
        return {"status": "unavailable", "latency_ms": elapsed}


async def run_all_checks(db: AsyncSession) -> list[dict]:
    checks = {
        "database": _check_db(db),
        "redis": _check_redis(),
        "minio": _check_minio(),
        "qdrant": _check_qdrant(),
        "ollama": _check_ollama(),
    }
    results = await asyncio.gather(*checks.values(), return_exceptions=True)
    output = {}
    for name, result in zip(checks, results):
        if isinstance(result, Exception):
            logger.error("Unexpected health check error", service=name, error=str(result))
            output[name] = {"status": "error", "latency_ms": -1, "detail": str(result)}
        else:
            output[name] = result
    return output
