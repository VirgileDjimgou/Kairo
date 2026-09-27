# ADR-009: Internal Domain Events And PostgreSQL-Backed Outbox

Status: Accepted

## Context

Business modules (receipt declaration, validation, custody handover) previously
called audit persistence and notification helpers directly inside their command
methods. That coupled finance commands to secondary-effect implementations and made
retry behaviour implicit: a retried request could duplicate audit history, and there
was no single record of which projections a committed business fact still owed.

Notification delivery already used a PostgreSQL transactional outbox (ADR-004). The
same durability and idempotency guarantees are needed for audit projection, recipient
resolution and custody notices.

## Decision

- `services/api/app/modules/domain_events/` owns a lightweight internal event log in
  the existing PostgreSQL database. No broker, no Kafka, no microservices.
- A `DomainEvent` row carries event id, tenant id, actor, event type, aggregate
  type/id, `occurred_at`, the request `correlation_id`, a per-tenant deduplication
  key, a JSON payload, the list of already-applied handlers, and the outbox
  status/attempts/backoff fields.
- Events are written in the caller's transaction. Registered consumer handlers run
  inline when possible; anything left pending is retried by the Celery task
  `domain_events.process_outbox`. A committed business mutation therefore always has
  a durable event, while a consumer failure never rolls the mutation back.
- Consumers register in their own module and are composed lazily by
  `domain_events.registry.default_registry()`:
  - `audit.receipt_projection` writes the tenant audit trail with the event id as an
    idempotency key (`audit_events.deduplication_key`, unique per tenant);
  - `notifications.receipt_inbox` resolves recipients and enqueues the existing
    notification outbox (ADR-004) with stable deduplication keys;
  - `notifications.custody_notice` sends the treasury custody email and records its
    delivery outcome.
- Business modules publish facts only. They do not import audit services, notification
  services or delivery providers.
- Retries are safe: the outbox records applied handlers, emit is idempotent per
  `(tenant_id, deduplication_key)`, audit projection is idempotent by event id, and the
  notification outbox is idempotent by its own deduplication key. Financial mutations
  (payment creation, contribution balance updates) stay inside the original synchronous
  command and are never re-executed by event handlers.

## Consequences

- The receipt lifecycle (declared, updated, submitted, processed/validated, handover
  reported, reminder updated, treasury closure) emits domain events; audit and
  notification behaviour is unchanged for API clients.
- At-least-once dispatch cannot duplicate audit history, inbox events or money because
  every consumer is idempotent and no handler performs a financial mutation.
- The same pattern can absorb the remaining direct audit projections in other modules
  without changing the event model.
- Roadmap V2 S114 builds the unified notification platform on top of these events.
