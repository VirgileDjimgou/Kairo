# ADR-010: Unified Notification Pipeline, Profile-Bound Push, Safe Deep Links

Status: Accepted

## Context

Kairo had two coexisting notification paths: the authenticated inbox/outbox pipeline
(Web Push + Android FCM) and the operator channel dispatcher (email/Telegram/WhatsApp).
Producers wrote envelope fields ad hoc, push transports were hard-wired inside the
outbox worker, FCM invalid tokens were never disabled, and sign-out left push bindings
active. Sprint 113 introduced internal domain events; Sprint 114 converges the
notification platform on that foundation without a greenfield rewrite.

## Decision

- **One canonical pipeline.** Business facts flow through domain events →
  `notifications.receipt_inbox` / `notifications.finance_records` /
  `notifications.custody_notice` consumers or, for non-event producers (announcements,
  events, disciplinary, scheduled reminders), through
  `UserNotificationService.notify(...)`. `PolicyMixin.notify` is the only writer of
  recipient outbox events and is idempotent per `(tenant_id, deduplication_key)`.
- **Canonical envelope.** `NotificationOutboxEvent` payloads and `UserNotification`
  rows carry notification id, event id, tenant id, recipient, category, priority,
  event type, target path, timestamps, deduplication key, correlation id and metadata;
  `push_policy` marks push as a generic delivery hint.
- **Authenticated detail, generic push.** Push bodies are always
  `Kairo / Une nouvelle notification est disponible.` plus a safe internal
  `target_path`. Finance and disciplinary detail stays behind authentication.
- **Replaceable transports.** Web Push (VAPID, standards-based) and Android FCM
  (Firebase Admin, HTTP v1) are provider protocols in `app/providers/push/` with real
  and fake implementations. Web Push is not migrated to Firebase. Permanently invalid
  targets (Web Push 404/410, FCM unregistered/sender-mismatch) are disabled;
  transient errors use bounded retry with backoff.
- **Profile-scoped binding and sign-out.** Push bindings live on
  `NotificationDeviceProfile`. Sign-out (Vue `auth.store.logout()`, Flutter
  `DeviceRegistration.revokeForSession`) calls
  `POST /notifications/devices/{installation_id}/revoke`, which revokes that user's
  profile on the installation and disables their subscriptions. The installation
  identity is preserved, so a later sign-in re-registers and re-enables delivery.
  Shared devices keep other accounts' bindings intact.
- **Safe deep links.** Notification `target_path` values are internal absolute paths.
  The service worker validates origin and path before navigation, the Vue inbox
  resolves targets against the authenticated router, and Flutter maps only explicit
  first-segment allowlisted paths to shell destinations.
- **Observability.** `/metrics` exposes outbox pending/failed/oldest-age,
  push delivery outcomes and disabled subscription counters;
  `GET /notifications/health` (tenant administration) exposes configuration status,
  worker liveness, queue depth and invalid subscriptions without keys or tokens.

## Consequences

- Producers no longer duplicate recipient policy or transport code.
- At-least-once dispatch cannot duplicate inbox items; retries are bounded.
- A signed-out browser or Android installation stops receiving authenticated hints.
- The operator channel dispatcher (email/Telegram/WhatsApp) remains a separate
  operator surface; it reuses the same provider abstraction conventions but is not
  an inbox transport.
- Security/account self-notifications are not pushed today; they remain in the
  authenticated account-security view and audit trail (see the event matrix).
