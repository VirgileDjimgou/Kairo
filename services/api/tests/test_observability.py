"""Sprint 23 tests: observability, correlation IDs, and runtime visibility."""

import uuid as _uuid

import pytest
from httpx import AsyncClient

from app.modules.documents.models import IngestionJob
from helpers import create_tenant_with_user, login

pytestmark = pytest.mark.integration


def _metric_value(text: str, metric_name: str, labels: str | None = None) -> float:
    prefix = metric_name if labels is None else f"{metric_name}{labels}"
    for line in text.splitlines():
        if line.startswith(prefix):
            return float(line.split()[-1])
    raise AssertionError(f"Metric not found: {prefix}")


@pytest.mark.asyncio
async def test_http_errors_include_request_id_and_error_code(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    response = await client.post(
        "/api/v1/documents/upload",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Request-ID": "req-observability-001",
        },
        files={"file": ("blocked.exe", b"MZ", "application/octet-stream")},
        data={"title": "Blocked", "access_scope": "tenant_public"},
    )
    assert response.status_code == 400, response.text
    assert response.headers["X-Request-ID"] == "req-observability-001"
    assert response.headers["X-Error-Code"] == "bad_request"
    body = response.json()
    assert body["request_id"] == "req-observability-001"
    assert body["error_code"] == "bad_request"
    assert body["detail"] == "Unsupported file extension"


@pytest.mark.asyncio
async def test_validation_errors_use_structured_taxonomy(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("policy.txt", b"tenant body", "text/plain")},
        data={"description": "Missing title should trigger validation"},
    )
    assert response.status_code == 422, response.text
    assert response.headers["X-Error-Code"] == "validation_error"
    body = response.json()
    assert body["error_code"] == "validation_error"
    assert body["request_id"]
    assert isinstance(body["detail"], list)


@pytest.mark.asyncio
async def test_metrics_and_ingestion_health_surface_job_state(
    client: AsyncClient, db_session
) -> None:
    data = await create_tenant_with_user(db_session, f"obs-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("ops.txt", b"operations body", "text/plain")},
        data={"title": "Operations Doc", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text
    job_id = _uuid.UUID(upload.json()["ingestion_job_id"])

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    job.status = "failed"
    job.error_message = "parser timeout"
    await db_session.commit()

    health_before = await client.get(
        "/api/v1/admin/ingestion-jobs/health",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert health_before.status_code == 200, health_before.text
    before_body = health_before.json()
    assert before_body["failed_count"] == 1
    assert len(before_body["recent_failures"]) == 1

    retry = await client.post(
        f"/api/v1/documents/ingestion-jobs/{job_id}/retry",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert retry.status_code == 200, retry.text
    assert retry.json()["retried"] is True

    health_after = await client.get(
        "/api/v1/admin/ingestion-jobs/health",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert health_after.status_code == 200, health_after.text
    after_body = health_after.json()
    assert after_body["queued_count"] == 1
    assert after_body["failed_count"] == 0
    assert after_body["retried_count"] == 1

    baseline_metrics = await client.get("/metrics")
    baseline_text = baseline_metrics.text
    baseline_retries = _metric_value(
        baseline_text,
        "kairo_ingestion_retries_total",
    )

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    job.status = "failed"
    job.error_message = "parser timeout"
    await db_session.commit()

    retry_again = await client.post(
        f"/api/v1/documents/ingestion-jobs/{job_id}/retry",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert retry_again.status_code == 200, retry_again.text

    metrics_response = await client.get("/metrics")
    assert metrics_response.status_code == 200, metrics_response.text
    metrics_text = metrics_response.text
    assert "kairo_http_requests_total" in metrics_text
    assert 'kairo_ingestion_jobs_total{status="queued"} 1' in metrics_text
    assert _metric_value(metrics_text, "kairo_ingestion_retries_total") == baseline_retries + 1


@pytest.mark.asyncio
async def test_health_reports_degraded_dependency(monkeypatch, client: AsyncClient) -> None:
    async def fake_checks(db):
        return {
            "database": {"status": "ok", "latency_ms": 1},
            "redis": {"status": "unavailable", "latency_ms": 2},
            "minio": {"status": "ok", "latency_ms": 3},
            "qdrant": {"status": "ok", "latency_ms": 4},
            "ollama": {"status": "ok", "latency_ms": 5},
        }

    monkeypatch.setattr("app.main.run_all_checks", fake_checks)

    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["checks"]["redis"]["status"] == "unavailable"
