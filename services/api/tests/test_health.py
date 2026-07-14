"""Sprint 35: health endpoint with real dependency probes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
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
    assert "modules" in body
    assert body["status"] in ("ok", "degraded", "unavailable")


@pytest.mark.asyncio
async def test_health_all_expected_services_present(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    required_services = {"database", "redis", "minio", "qdrant", "llm_provider", "embedding_provider"}
    assert required_services.issubset(body["checks"].keys())


@pytest.mark.asyncio
async def test_health_each_service_has_status_and_latency(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    for svc, check in body["checks"].items():
        assert "status" in check, f"{svc} missing status"
        assert "latency_ms" in check, f"{svc} missing latency_ms"
        assert check["status"] in ("ok", "degraded", "unavailable", "error")


@pytest.mark.asyncio
async def test_health_database_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    db_check = body["checks"]["database"]
    assert db_check["status"] == "ok"
    assert db_check["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_health_external_services_report_unavailable_in_test(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    for svc in ("redis", "minio", "qdrant", "llm_provider", "embedding_provider"):
        check = body["checks"].get(svc)
        assert check is not None, f"{svc} missing from checks"
        assert check["status"] in ("unavailable", "error"), (
            f"Expected {svc} to be unavailable without Docker, got {check['status']}"
        )


@pytest.mark.asyncio
async def test_health_overall_is_unavailable_when_services_down(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    assert body["status"] == "unavailable"


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_format(client: AsyncClient) -> None:
    response = await client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "# HELP" in text
    assert "kairo_" in text
