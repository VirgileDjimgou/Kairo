# ADR-015: Notification Deep-Link Allowlisting And Inbox Fallback

Status: Accepted (extends ADR-010)

## Context

The notification pipeline (ADR-010) already keeps push payloads generic and
resolves recipients server-side. Notification interaction still needed a single,
enforceable contract for targets: producers could enqueue any `target_path`, the
client accepted any same-origin path, and an inaccessible target (forbidden
role, disabled module, removed route) redirected to the dashboard instead of the
notification the user clicked.

Deep links are an untrusted input: a payload, a stale route or a producer bug
must never be able to navigate the PWA to an external address or dump the user
on an unrelated page.

## Decision

- **Backend allowlist.** `app/modules/notifications/deep_links.py` defines the
  internal destination prefixes a notification may reference. Every enqueue
  normalizes `target_path` through `resolve_target_path()`; unknown, external,
  protocol-relative or traversal-like values become `/notifications`. Prefix
  matching is boundary-aware (`/finance` matches `/finance/...` but not
  `/finance-secret`).
- **Canonical envelope.** Outbox payloads carry `envelope_version: 1` plus the
  existing envelope (`event_id`, `category`, `priority`, `target_path`,
  `metadata` as safe non-secret context, `correlation_id`, `push_policy`);
  `notification_id` remains the per-recipient inbox identity and `tenant_id` the
  row scope.
- **Client route validation.** `resolveNotificationTarget()` validates the
  target against the actual Vue Router, the current authentication state, the
  role/module meta of the matched route and the tenant module toggles. An
  unsafe, unknown, redirected or inaccessible target resolves to the
  authenticated inbox.
- **Inbox fallback everywhere.** The Service Worker default target, the
  `notificationclick` handler, the in-app navigation message listener and the
  inbox item click all fall back to `/notifications`. An unauthenticated target
  still survives sign-in through `/login?redirect=<target>`.
- **Privacy-safe push.** Push payloads carry only a generic title/body and the
  allowlisted target. Amounts, names, sanction reasons and other detail remain
  in the authenticated inbox; the deep link is a hint, not a data channel.

## Consequences

- Every notification target is either an allowlisted internal route or the
  authenticated inbox; no payload can trigger an external navigation.
- Authorization is unchanged: the backend still authorizes every request and
  the router guard still enforces authentication, tenant and module state. The
  client pre-check only decides between the exact target and the inbox.
- Producers keep using their existing paths; an unknown path fails safe instead
  of raising, so a business operation is never rolled back by a navigation bug.
- Representative business cases (payment, contribution, receipt declaration,
  validation/rejection, cash handover, treasury confirmation, expense,
  announcement, event, disciplinary, administrative) are covered by backend
  allowlist tests and client fallback tests.
