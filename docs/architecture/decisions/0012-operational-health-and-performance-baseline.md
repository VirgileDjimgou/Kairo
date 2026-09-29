# ADR-012: Operational Health, Pipeline Metrics And A Committed Performance Baseline

Status: Accepted

## Context

Sprints 110–115 hardened behaviour (bounded contexts, domain events, unified
notifications, contract boundary), but operators still had limited answers to
"why is Kairo unhealthy?" and no way to detect performance regressions. The
notification outbox had per-tenant health only, the domain-event outbox had no
health surface at all, `/health` never failed and had no readiness semantics,
Celery work was not correlated with the request that caused it, and no
representative performance measurement existed.

## Decision

- **Layered health endpoints.**
  - `/health` stays HTTP 200 with an overall `status` for the existing PWA and
    scripts, and now includes `backup`, `notification_outbox` and
    `domain_event_outbox` checks with safe counts and ages.
  - `/health/live` is a process liveness probe (always 200 while the API
    answers).
  - `/health/ready` gates on the critical dependencies (`database`, `redis`) and
    returns HTTP 503 `not_ready` when one is down, for load balancers and
    orchestration.
  - Operational checks report `degraded` for actionable backlog/staleness rather
    than marking the service unavailable, except when the probe itself fails.
- **Pipeline and backup metrics.** `/metrics` gains domain-event outbox
  pending/failed/oldest-age, notification outbox processing, and backup
  age/failed-run gauges, plus Grafana panels. Metrics remain free of tenant,
  member, message and token labels; a regression test asserts that distinctive
  tenant/member markers never appear in the scrape output.
- **Celery correlation.** Worker processes configure structured logging and bind
  `task_id`, `task_name` and a `kairo_correlation_id` header (taken from the
  originating request) for the duration of each task. Outbox consumers log
  event id, type, attempt and exception class on failure — never payloads.
- **Committed performance baseline.** A deterministic harness
  (`services/api/scripts/performance_baseline.py`) seeds 200- and 1000-member
  tenants with three years of finance history and records p50/p95 latency and
  SQL statement counts for representative operations into
  `docs/performance/performance-baseline.json` and
  `docs/performance/PERFORMANCE_BASELINE.md`. `npm run perf:check` compares a
  fresh 200-member run against committed thresholds. Statement counts are the
  primary regression signal; latency keeps a 4x margin.
- **Obvious N+1 fixes** land with query-count regression tests: batched role
  lookup for the managed-user directory, batched reachability for unreachable
  notifications, one profile query for batch reminders, and no duplicated
  queries in member statements. Composite indexes cover the hot filters.

## Consequences

- An operator can determine dependency readiness, pipeline backlog, backup
  freshness and AI-runtime state from one page and one scrape.
- Health checks never leak member data; details are counts and timestamps.
- Absoulte latencies are machine-dependent, so the performance gate is an
  opt-in local command rather than CI, while statement counts give a
  deterministic drift signal.
- The performance harness is the reference for future 1000-member regression
  work (Sprint 118).
