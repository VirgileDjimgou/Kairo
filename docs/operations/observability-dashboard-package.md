# Observability Dashboard Package

Sprint 80 packages Kairo's existing runtime observability into a reusable
Prometheus and Grafana baseline for disciplined self-hosted operators.

## What This Package Includes

- `infra/monitoring/prometheus.yml`
- `infra/monitoring/docker-compose.monitoring.yml`
- `infra/monitoring/grafana/provisioning/datasources/prometheus.yml`
- `infra/monitoring/grafana/provisioning/dashboards/dashboards.yml`
- `infra/monitoring/grafana/dashboards/kairo-operator-overview.json`

The package is intentionally narrow:

- it scrapes the existing API `/metrics` endpoint
- it does not bypass backend authorization or expose tenant-private business data
- it visualizes only the runtime and pipeline signals already emitted by Kairo

## Dashboard Scope

The bundled Grafana dashboard focuses on operator questions that already map to
the current codebase:

- Is the API receiving traffic?
- Are structured errors increasing?
- Is average request latency drifting upward?
- Are ingestion jobs failing or backing up?
- Are retries increasing?
- Is the chatbot workload increasing, and are refusals climbing?

This package does not mirror tenant-private financial, disciplinary, or member
data. It is safe by design because it uses only operational metrics already
exported by `/metrics`.

## Startup

From the repository root:

```bash
docker compose -f docker-compose.yml -f infra/monitoring/docker-compose.monitoring.yml up -d
```

Expected local URLs:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Default Grafana credentials can be overridden with:

- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`

## Metric Mapping

Dashboard panels map directly to the current API runtime metrics:

| Dashboard concern | Metric(s) |
|---|---|
| HTTP request volume | `kairo_http_requests_total` |
| Average request latency | `kairo_http_request_latency_ms_sum`, `kairo_http_request_latency_ms_count` |
| Structured errors | `kairo_error_total` |
| Ingestion runtime backlog | `kairo_ingestion_jobs_total` |
| Ingestion retries | `kairo_ingestion_retries_total` |
| Chat workload | `kairo_chat_queries_total` |
| Chat refusals | `kairo_chat_queries_refused_total` |

## How To Read It With `/health`

Use the dashboard and the health endpoints together:

1. Check Grafana for request, error, ingestion, and refusal trends.
2. Check `GET /health` for dependency status and latency.
3. Check the admin health center for tenant-entered recovery evidence and alert posture.
4. Use `X-Request-ID` from a failing response to correlate logs and operator reports.

## Validation Contract

The backend test suite now verifies that:

- the packaged dashboard exists
- every `kairo_*` metric referenced by the dashboard is actually emitted by `/metrics`
- the Prometheus scrape configuration targets the API `/metrics` endpoint

This gives the monitoring package a real regression guard instead of relying on
documentation alone.

