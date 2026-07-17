"""Sprint 80 tests: packaged observability assets must match runtime metrics."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = REPO_ROOT / "infra" / "monitoring" / "grafana" / "dashboards" / "kairo-operator-overview.json"
PROMETHEUS_CONFIG_PATH = REPO_ROOT / "infra" / "monitoring" / "prometheus.yml"
METRIC_NAME_PATTERN = re.compile(r"\bkairo_[a-z0-9_]+\b")


def _extract_metric_names_from_dashboard() -> set[str]:
    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    names: set[str] = set()
    for panel in dashboard.get("panels", []):
        for target in panel.get("targets", []):
            expr = target.get("expr", "")
            names.update(METRIC_NAME_PATTERN.findall(expr))
    return names


def _extract_metric_names_from_payload(payload: str) -> set[str]:
    names: set[str] = set()
    for line in payload.splitlines():
        if not line or line.startswith("#"):
            continue
        metric_name = line.split("{", 1)[0].split(" ", 1)[0]
        names.add(metric_name)
    return names


def test_packaged_dashboard_and_prometheus_config_exist() -> None:
    assert DASHBOARD_PATH.exists(), f"Missing dashboard package: {DASHBOARD_PATH}"
    assert PROMETHEUS_CONFIG_PATH.exists(), f"Missing Prometheus config: {PROMETHEUS_CONFIG_PATH}"


@pytest.mark.asyncio
async def test_packaged_dashboard_only_references_runtime_metrics(client: AsyncClient) -> None:
    await client.get("/health")
    await client.get("/metrics")
    await client.get("/definitely-missing-route")

    response = await client.get("/metrics")
    assert response.status_code == 200, response.text

    dashboard_metrics = _extract_metric_names_from_dashboard()
    runtime_metrics = _extract_metric_names_from_payload(response.text)

    assert dashboard_metrics, "Dashboard should reference at least one kairo_* metric"
    assert dashboard_metrics.issubset(runtime_metrics), (
        f"Dashboard references metrics not emitted by /metrics: {sorted(dashboard_metrics - runtime_metrics)}"
    )


def test_prometheus_package_scrapes_api_metrics_endpoint() -> None:
    config = PROMETHEUS_CONFIG_PATH.read_text(encoding="utf-8")
    assert 'job_name: "kairo-api"' in config
    assert "metrics_path: /metrics" in config
    assert "api:8000" in config
