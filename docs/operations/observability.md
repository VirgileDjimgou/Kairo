# Observability And Runtime Support

Last verified: 2026-09-27 (Roadmap V2 Sprint 116).

## Health, liveness and readiness

- `GET /health` — full operational picture. Per-service checks:
  - `database`, `redis`, `minio`, `qdrant`, `llm_provider`, `embedding_provider`
    (external dependencies; optional AI checks report `disabled` when the AI
    runtime is off)
  - `backup` — last successful backup age; `degraded` when stale (> 7 days) or
    never recorded; `disabled` when backups are turned off
  - `notification_outbox` — pending/failed counts and oldest pending age;
    `degraded` on terminal failures or a backlog older than 5 minutes
  - `domain_event_outbox` — same semantics for internal domain events
  - Each probe returns `status` (`ok`, `degraded`, `unavailable`, `disabled` or
    `error`), `latency_ms`, and safe counts only (never recipients, tokens or
    message content).
- `GET /health/live` — process liveness; always HTTP 200 while the API answers.
- `GET /health/ready` — readiness for traffic. Gates on `database` and `redis`;
  returns HTTP 200 `ready` or HTTP 503 `not_ready` with per-dependency status.
  Use this for load balancers and container orchestration.
- The existing `/health` contract stays HTTP 200 with an overall `status`
  (`ok` | `degraded` | `unavailable`) for backward compatibility with the PWA
  health center.

## Metrics

`GET /metrics` returns Prometheus-style text metrics:

- HTTP request volume by method and status class, latency sum/count, structured
  error counts by `error_code`
- ingestion job counts by runtime status and ingestion retry counts
- chat query and refused query totals
- push delivery outcomes (`kairo_push_deliveries_total` plus per-channel success
  and failure aliases) and disabled Web Push/FCM counters
- notification outbox: pending, processing, failed, oldest pending age
- domain event outbox: pending, failed, oldest pending age
- backup: last successful age and failed run count

Metrics never carry tenant, member, message or token labels; only statuses,
counts and metric names. Pipeline backlog and backup metrics are also rendered
in the bundled Grafana dashboard (`infra/monitoring/`).

## Correlation IDs and structured logging

- Every response includes `X-Request-ID`; clients may supply their own and it is
  echoed back. Errors also include `error_code` and `request_id`.
- The request id is stored in a contextvar, persisted on domain events
  (`correlation_id`) and notification outbox payloads, and exposed on inbox
  items, so an operator can trace an HTTP request through asynchronous
  consumers.
- Ingestion tasks carry the originating request id in Celery headers
  (`kairo_correlation_id`). Worker processes configure structured logging and
  bind `task_id`, `task_name` and `correlation_id` for the duration of each
  task; outbox consumers log only event id/type/attempts/exception class on
  failure initial delivery and handler retries — never payload content.

## Privacy-Safe Review Surfaces

- Admin chat traceability shows minimized question/answer previews, refusal
  previews, source types and citation counts.
- Audit event review and CSV export redact sensitive member-facing detail
  fields before display or export.
- Health and metrics surfaces expose counts and ages only.

## Operator Surfaces

- Admin health center (`/admin/health`): dependency checks (including backup,
  notification outbox and domain event outbox), recovery evidence, freshness
  warnings and a notification pipeline card (worker running, pending, failed,
  oldest pending).
- Admin notifications console: operator channel history/reconciliation plus
  notification pipeline health.
- `GET /api/v1/notifications/health` (tenant administration): Web Push/Firebase
  configured, worker liveness heuristic, outbox depth and disabled subscription
  counts.

## Performance Baseline

- `npm run perf:baseline` — deterministic 200/1000-member datasets with
  three years of finance history; records p50/p95 latency and SQL statement
  counts per representative operation in
  `docs/performance/performance-baseline.json` and
  `docs/performance/PERFORMANCE_BASELINE.md`.
- `npm run perf:check` — reruns the 200-member workload and fails when p95 or
  statement counts exceed the committed thresholds. This is an opt-in local
  regression signal, not generic CI.
- Statement counts are the primary regression signal; latency thresholds keep a
  4x margin because absolute timings depend on the machine.

## Support Workflow

When diagnosing an incident:

1. `GET /health/ready` for traffic-readiness; `GET /health` for the full picture
   (including backup, notification and domain-event pipeline status).
2. `GET /metrics` for error growth, outbox backlog/age, backup age and retry
   spikes.
3. `GET /api/v1/admin/ingestion-jobs/health` for the document pipeline.
4. Use the response `request_id` (and inbox `correlation_id`) to correlate API
   logs with worker task logs.
5. Review admin chat traceability and audit exports through the privacy-safe
   summaries, not raw private payloads.

## Alerting Guidance

Suggested alerts for small deployments:

- database or Redis readiness probe fails (`/health/ready` != 200)
- `kairo_notification_outbox_failed` or `kairo_domain_event_outbox_failed` > 0
- `kairo_notification_outbox_oldest_age_seconds` > 900
- `kairo_backup_last_success_age_seconds` > 604800 (7 days)
- repeated 5xx errors on the API
- ingestion failed job count trending upward

## Notes

- Metrics are lightweight, process-local and local-first; with multiple API
  workers each scrape reflects one process.
- The bundled Prometheus/Grafana package (`infra/monitoring/`) includes the
  outbox and backup panels, and a backend regression test ensures the dashboard
  references only metrics that `/metrics` actually emits.
