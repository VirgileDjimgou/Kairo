# Notification Event Matrix

Last verified: 2026-10-03 (Roadmap V2 Sprint 122)

Every row is backend-owned. Clients never decide recipients or access; push payloads
are generic delivery hints and all detail is read from the authenticated inbox.

## Pipeline

```
Business operation / scheduled worker
        |
Domain event (S113) or direct producer for non-event domains
        |
Notification policy + recipient resolver      UserNotificationService.notify(...)
        |
Transactional notification outbox (NotificationOutboxEvent)
        |
Authenticated inbox (UserNotification)  +  Push delivery (outbox worker)
                                              |            |
                                        Web Push VAPID   Android FCM (Firebase Admin HTTP v1)
                                              |            |
                                        Browser          Firebase
                                              |
                                   authenticated deep link
```

## Canonical envelope

| Field | Where | Notes |
| --- | --- | --- |
| `envelope_version` | outbox payload | Canonical envelope revision (currently `1`). |
| `notification_id` | `user_notifications.id` | Stable inbox identity. |
| `event_id` | `user_notifications.event_id`, outbox payload | Domain event id when the producer is event-driven. |
| `tenant_id` | both tables | Every query is tenant-scoped. |
| `recipient_user_id` | `user_notifications.recipient_user_id` | Resolved by the policy layer, never by clients. |
| `category` | `finance`, `discipline`, `announcements`, `events` | Drives per-profile preference filtering. |
| `priority` | `normal` / `high` | Presentation hint only. |
| `event_type` | e.g. `finance.receipt_validated` | Client label lookup key. |
| `target_path` | allowlisted internal path | Normalized server-side by `deep_links.resolve_target_path()`; unknown/external values become `/notifications`. Re-validated by the client against the router and current authorization. |
| `created_at` | both tables | Ordering and staleness. |
| `deduplication_key` | outbox + per recipient | Idempotency; retries cannot duplicate. |
| `correlation_id` | request `X-Request-ID` | End-to-end traceability. |
| `metadata` (safe metadata) | JSON | Safe, non-secret context (amount/category/income type). Never pushed. |
| `push_policy` | `generic` | No sensitive content is ever pushed. |

## Deep-link contract

```text
producer target_path
      |
      v
backend allowlist (deep_links.resolve_target_path)   unknown/external -> /notifications
      |
      v
outbox payload -> authenticated inbox item + generic push (target only)
      |
      v
Service Worker safeTarget()                          unsafe/missing -> /notifications
      |
      v
client resolveNotificationTarget()                   unknown/forbidden/redirect -> /notifications
      |
      v
Vue Router guard -> FastAPI authorization -> exact target
```

- Unauthenticated targets survive sign-in through `/login?redirect=<target>`.
- An inaccessible target (role, module toggle, removed route) falls back to the
  authenticated inbox instead of the dashboard.
- Decision record: ADR-015.

## Event matrix

| Producer | Event / trigger | Category | Eligible recipients | Inbox | Web Push | Android FCM | Deep link | Privacy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Finance receipt command (domain event `finance.receipt_declared`) | Receipt declared | finance | Active `treasurer`, `principal_admin` in tenant | Yes | Yes (generic) | Yes (generic) | `/finance` | High: amount only in authenticated inbox |
| Finance receipt command (domain events `finance.receipt_{validated,partially_validated,rejected,clarification_requested,cancelled}`) | Receipt processed | finance | Declarant + linked member user | Yes | Yes (generic) | Yes (generic) | `/finance` | High |
| Scheduled worker `contributions.send_due_receipt_handover_reminders` | Cash handover due | finance | Declarant + linked member user | Yes | Yes (generic) | Yes (generic) | `/finance` | High |
| Custody command `receipt_handover_reminder_updated` | Handover deadline updated | finance | Declarant + linked member (email notice + delivery audit) | No (email only) | No | No | — | High |
| Custody command `finance.receipt_received_in_treasury` | Treasury receipt confirmed / cash handover completed | finance | Declarant + linked member user | Yes | Yes (generic) | Yes (generic) | `/finance` | High |
| Finance contribution command (domain event `finance.payment_recorded`) | Payment recorded on a member account | finance | Linked member user (self) | Yes | Yes (generic) | Yes (generic) | `/finance` | High |
| Finance expense command (domain event `finance.expense_recorded`) | Expense recorded | finance | Active `auditor` in tenant | Yes | Yes (generic) | Yes (generic) | `/finance` | High (auditor oversight) |
| Announcements service | Announcement published / updated (public or members-only) | announcements | All active tenant users | Yes | Yes (generic) | Yes (generic) | `/announcements` | Normal |
| Events service | Event published / updated (public or members-only) | events | All active tenant users | Yes | Yes (generic) | Yes (generic) | `/events` | Normal |
| Disciplinary service | Disciplinary record created / updated | discipline | Linked member user only | Yes | Yes (generic) | Yes (generic) | `/discipline` (web alias; Flutter governance) | Very high: no detail in push |
| Identity / account security | Password change, session revocation, MFA change, recovery | — | Affected user | No (deliberate) | No | No | Account security view + audit trail | High: never on a lock screen |
| Finance reminders (operator email) | Contribution reminder sent | — | Chosen single member / outstanding cohort | No | No | No | — | Operator channel, audited |
| Operator dispatch console | Manual email/Telegram/WhatsApp | — | Operator-selected recipient | No | No | No | — | Operator channel, audited |

## Preference contract

Per user and tenant across all device profiles: `push_enabled`, `finance_enabled`,
`discipline_enabled`, `announcements_enabled`, `events_enabled`. Preferences filter
push delivery only; the authenticated inbox always records the event. The contract is
consumed by both the Vue PWA and the Flutter client.

## Device and token lifecycle

- Installation identity is random and never account-derived; it survives sign-out.
- Sign-out revokes the current profile binding on that installation
  (`POST /notifications/devices/{installation_id}/revoke`).
- A shared installation keeps other accounts' bindings; a shared browser endpoint is
  delivered once per event even when several bound profiles are recipients.
- Web Push 404/410 and FCM unregistered/sender-mismatch disable the subscription;
  registration clears `disabled_at` and re-enables the profile.
- Transient push errors retry up to three times with backoff inside one outbox
  dispatch, then increment `failure_count`; the inbox event is already committed.

## Security events rationale

Account/security events are intentionally not pushed: a lock-screen hint would leak
that a security change occurred on the device. They remain visible in the
authenticated Account Security view and the tenant audit trail. Adding an
authenticated self-inbox notification for them is a future convergence item.
