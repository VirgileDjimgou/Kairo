"""Sprint 0 acceptance test: API health endpoint."""

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
    assert "checks" in body
    assert body["status"] in ("ok", "degraded")


@pytest.mark.asyncio
async def test_health_database_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    # DB must be reachable in CI / local Docker
    assert body["checks"]["database"] == "ok"
    assert body["status"] == "ok"
