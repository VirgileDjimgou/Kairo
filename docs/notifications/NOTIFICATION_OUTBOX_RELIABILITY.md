# Notification Outbox Reliability

Status: Active — Roadmap V2 Sprint 126
Related: ADR-004/ADR-010 (transactional notification outbox), ADR-009 (domain
events), `docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`

The notification outbox guarantees that a committed business operation always
has its inbox projection and push hint, even when a worker crashes. This
document defines the lease, retry and dead-letter behavior; the same principles
apply to the domain-event outbox.

## Processing lease and reclaim

- Claiming an event sets `status=processing`, increments `attempts` and records
  `processing_started_at`.
- The lease duration is `OUTBOX_PROCESSING_LEASE_SECONDS` (default 300).
- Before every batch, `reclaim_stale_events()` returns rows whose
  `processing_started_at` is older than the lease to `pending`
  (`available_at=now`, `last_error=stale_processing_reclaimed`). A crashed
  worker therefore cannot strand an event permanently; the next worker run
  reclaims and delivers it.
- The claim query still uses `FOR UPDATE SKIP LOCKED`, so concurrent workers
  never process the same live row.

## Retry policy, backoff and dead-letter

- Transient delivery failures keep the event `pending` with exponential backoff
  (`2^attempts` minutes, capped at 30) until `attempts` reaches 5.
- The fifth failure moves the event to the terminal `failed` state
  (dead-letter). `last_error` persists the exception class or handler name and
  `processing_started_at` is cleared.
- `notifications.reconcile_user_outbox` runs every 300 seconds, reclaims expired
  leases and logs a structured report even when no new events exist.

## Idempotent delivery

- The inbox projection is idempotent: each recipient row carries a unique
  `(tenant_id, deduplication_key)` key and `_deliver_event` skips rows that
  already exist, so a reclaimed or retried event never duplicates a
  notification.
- Push is a delivery hint and remains **at-least-once**: a crash between the
  inbox commit and the push may re-send the generic push. The authenticated
  inbox is always the single source of truth, and push bodies never contain
  sensitive detail.
- Domain events record applied handler names, so a retry re-runs only handlers
  that did not complete.

## Operator visibility

- `GET /notifications/health` exposes `stranded_outbox` (processing beyond the
  lease), `retrying_outbox` (pending with attempts > 0) and `failed_outbox`
  (dead-letter).
- `/health` reports the notification outbox detail with `pending`, `failed`,
  `stranded`, `retrying` and `oldest_pending_seconds`.
- `/metrics` exposes `kairo_notification_outbox_pending`,
  `kairo_notification_outbox_processing`,
  `kairo_notification_outbox_stranded`,
  `kairo_notification_outbox_retrying`,
  `kairo_notification_outbox_failed`,
  `kairo_domain_event_outbox_stranded` and the existing domain-event gauges.
- No metric or log contains notification content, tokens or member data.

## Verification

`services/api/tests/test_outbox_reliability.py` proves: an expired lease is
reclaimed and delivered; a fresh lease is not; a reclaimed event does not
duplicate inbox rows; the fifth failure becomes dead-letter; health and
reconciliation expose stranded/retrying/dead-letter counts; and the domain-event
lease is reclaimed.

```bash
python -m pytest services/api/tests/test_outbox_reliability.py -q
```
