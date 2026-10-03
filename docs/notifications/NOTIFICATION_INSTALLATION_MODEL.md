# Notification Installation Model

Status: Active — Roadmap V2 Sprint 121
Related: ADR-010 (unified notification pipeline), ADR-014 (PWA-first),
`docs/pwa/PWA_ARCHITECTURE.md`, `docs/notifications/NOTIFICATION_EVENT_MATRIX.md`

The authenticated inbox is the source of truth. Push providers are delivery
hints only, and FastAPI remains the only recipient-resolution and authorization
authority. Firebase topics are never used as an access-control mechanism.

## Normalized model

| Concept | Table | Key fields |
| --- | --- | --- |
| Browser/Android installation | `notification_devices` | `tenant_id`, `installation_id` (random, never account identity), `platform`, `browser`, `user_agent`, `device_metadata_json`, `status` (`active`/`revoked`), `created_at`, `updated_at`, `last_seen_at`, `revoked_at` |
| Authenticated profile binding | `notification_device_profiles` | `tenant_id`, `device_id`, `user_id`, `push_enabled`, `preferences_json`, `opted_in_at`, `revoked_at` |
| Web Push (VAPID) subscription | `web_push_subscriptions` | `tenant_id`, `device_id`, `provider` (`web_push`), `endpoint`, `p256dh`, `auth`, `disabled_at`, `failure_count`, `created_at`, `updated_at` |
| Firebase token (Android or web) | `firebase_push_subscriptions` | `tenant_id`, `device_id`, `recipient_user_id`, `provider` (`firebase`), `platform`, `fcm_token`, `disabled_at`, `failure_count`, `created_at`, `updated_at` |

- One physical device may serve several Kairo accounts: each account has its own
  `notification_device_profiles` row and its own Firebase token binding. Web Push
  subscriptions are installation-level and deliver only to profiles that are
  active, push-enabled and preference-matching.
- `device_metadata_json` accepts at most 12 bounded string entries supplied by
  the client (language, display mode, screen, timezone). It is metadata only and
  is never used for authorization.

## Provider selection and duplicate prevention

1. **VAPID Web Push is the default browser transport** (standards-based; ADR-010
   explicitly keeps it).
2. **Firebase Web Messaging is the fallback** when VAPID is not configured but
   the public Firebase Web configuration is present. The FCM token is obtained
   through the canonical Service Worker registration, so background messages and
   VAPID push share one worker.
3. A recipient with an active web subscription and an active FCM token on the
   same installation receives **exactly one push**: the outbox records the
   `(recipient, installation)` pairs delivered through Web Push and skips the
   Firebase send for those pairs.

## Token and subscription lifecycle

- **Registration/renewal:** every explicit enablement and every application
  start (when permission is already granted) re-persists the current binding.
  Browser subscription rotation is captured by `pushsubscriptionchange`;
  FCM rotation re-requests the token and upserts it.
- **Token rotation:** saving a new FCM token disables obsolete active tokens for
  the same installation and profile, so a rotated token cannot double-deliver.
- **Invalid targets:** permanently invalid Web Push endpoints and FCM tokens are
  disabled; transient failures increment `failure_count` and are retried with
  bounded backoff by the outbox worker.
- **Logout / session revocation:** sign-out revokes this profile's binding on the
  installation. The installation identity and provider choice survive so a later
  sign-in re-enables delivery without a new permission prompt.
- **Tenant switching:** the previous tenant's binding is revoked **before** the
  tenant switch, and the existing provider is re-bound to the new tenant. A
  notification from a tenant the browser has left can never surface there.
- **Multi-profile safety:** revoking one profile only disables the shared web
  subscription when no other active profile remains on the installation.

## Retry telemetry

- The outbox records `attempts` and `last_error` per event; `failure_count`
  tracks per-subscription transient failures; `/metrics` exposes
  `web_push_success`/`web_push_failure`/`fcm_success`/`fcm_failure` and disabled
  gauges.
- `GET /notifications/health` additionally reports
  `retrying_web_subscriptions` and `retrying_fcm_tokens` (active targets with a
  non-zero failure count).
- The web client retries registration requests with bounded backoff and emits a
  `kairo:notification-registration-telemetry` event on recovery/failure. No
  notification content or token is ever placed in telemetry.

## Verification

- Backend: `services/api/tests/test_notification_installations.py` covers
  metadata normalization, multiple installations, multi-profile installations,
  tenant isolation for devices and tokens, token rotation, per-installation
  delivery deduplication, retry telemetry and endpoint validation.
- Web: `apps/web/e2e/notification-installations.spec.ts` covers metadata
  registration, stable installation identity, no first-visit permission prompt,
  explicit enablement without a provider, and revoke-before-switch ordering.
