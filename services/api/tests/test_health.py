"""Sprint 23: health endpoint with real dependency probes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_shape(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    assert "status" in body
    assert "version" in body
    assert "env" in body
    assert "checks" in body
    assert body["status"] in ("ok", "degraded", "unavailable")


@pytest.mark.asyncio
async def test_health_database_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    db_check = body["checks"]["database"]
    assert "status" in db_check
    assert "latency_ms" in db_check
    assert db_check["status"] == "ok"


@pytest.mark.asyncio
async def test_health_per_service_shape(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    required_services = {"database", "redis", "minio", "qdrant", "ollama"}
    assert required_services.issubset(body["checks"].keys())
    for svc, check in body["checks"].items():
        assert "status" in check, f"{svc} missing status"
        assert "latency_ms" in check, f"{svc} missing latency_ms"
        assert check["status"] in ("ok", "degraded", "unavailable", "error")
