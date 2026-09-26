# ADR-004: Transactional Notification Outbox, Push As Delivery Hint

Status: Accepted

## Context

Business operations (receipt validation, custody handover, announcements…) must
produce durable inbox notifications without coupling business code to delivery
transports (Web Push/VAPID, Android FCM, email providers).

## Decision

Notification side effects are written to a PostgreSQL-backed transactional
outbox in the same transaction as the business change, then dispatched by the
worker. The authenticated, tenant-scoped inbox is the source of detailed
information; push transports carry generic bodies and safe internal targets
only. Preferences are server-owned.

## Consequences

- Delivery failure never rolls back a committed business transaction.
- Outbox retries are idempotent via deduplication keys.
- Roadmap V2 S113/S114 generalize this outbox into internal domain events and a
  unified notification platform; the semantics above stay fixed.
