# Observability And Runtime Support

This document explains the operational visibility available in Kairo after Sprint 23.

## Health

- `GET /health`
- Returns per-service dependency probes for:
  - database
  - Redis
  - MinIO
  - Qdrant
  - Ollama
- Each probe includes:
  - `status`: `ok`, `degraded`, or `unavailable`
  - `latency_ms`
- The overall status is:
  - `ok` when every probe is healthy
  - `degraded` when at least one probe is degraded but none is hard down
  - `unavailable` when one or more probes are unavailable

## Metrics

- `GET /metrics`
- Returns Prometheus-style text metrics for:
  - HTTP request volume by method and status class
  - HTTP request latency aggregates
  - structured error counts
  - ingestion job counts by runtime status
  - ingestion retry counts from the audit trail
  - chat query and refused query totals

## Correlation IDs

- Every response includes `X-Request-ID`.
- Clients may provide their own `X-Request-ID`; the API will echo it back.
- Error responses also include:
  - `error_code`
  - `request_id`

## Ingestion Job Visibility

- Admin endpoint: `GET /api/v1/admin/ingestion-jobs/health`
- Returns:
  - queued job count
  - processing job count
  - failed job count
  - completed job count
  - retry count recorded through the audit trail
  - recent failed jobs

## Support Workflow

When diagnosing an incident:

1. Check `/health` for dependency status.
2. Check `/metrics` for growth in failed requests, ingestion backlog, or retry spikes.
3. Check `/api/v1/admin/ingestion-jobs/health` for document pipeline state.
4. Use the request ID from any failing response to correlate logs.

## Alerting Guidance

Suggested alerts for small deployments:

- database or Redis probe marked `unavailable`
- Qdrant or Ollama probe marked `unavailable`
- ingestion failed job count trending upward
- ingestion queued job count remaining high for an extended period
- repeated 5xx errors on the API

## Notes

- Metrics are intentionally lightweight and local-first.
- The first version is designed for operational clarity, not full enterprise telemetry.
