# Notification Operator Guide

Last verified: 2026-10-03 (Roadmap V2 Sprint 121)

Audience: self-hosting operators. This guide configures Web Push and Android FCM for
the Kairo FastAPI backend. It never asks you to commit credentials.

## 1. What runs where

| Component | Responsibility |
| --- | --- |
| FastAPI (`api`) | Writes the notification outbox inside the business transaction; serves the authenticated inbox, preferences, installation registration, `/notifications/health`. |
| Celery worker `domain_events.process_outbox` | Applies domain-event consumers (audit, inbox enqueue, custody notices). |
| Celery worker `notifications.process_user_outbox` | Creates inbox rows and sends Web Push + FCM; disables invalid targets and deduplicates per installation. |
| Vue PWA service worker | Displays generic push and opens the safe internal deep link. |
| Vue PWA client | Registers normalized installation metadata; uses VAPID Web Push by default and Firebase Web Messaging as the configured fallback; revokes its binding on sign-out and before tenant switching. |
| Flutter Android client (frozen reference) | Registers FCM tokens after explicit opt-in; revokes its binding on sign-out. |

Beat schedule: `process-user-notification-outbox` and `process-domain-event-outbox`
run every 15 seconds; `send-due-receipt-handover-reminders` every 60 seconds.

## 2. Web Push (VAPID)

Required environment variables (api + worker):

```dotenv
WEB_PUSH_ENABLED=true
WEB_PUSH_VAPID_PUBLIC_KEY=<public key>
WEB_PUSH_VAPID_PRIVATE_KEY=<private key>
WEB_PUSH_VAPID_SUBJECT=mailto:notifications@example.org
```

- Generate keys once with `python -m py_vapid --gen` (or `npx web-push
  generate-vapid-keys`). Store them only in the operator environment or secret
  mounts. The private key must never enter Git, the PWA bundle, or logs.
- The public key is served at runtime through
  `GET /api/v1/notifications/push/configuration`; it is not a build-time variable.
- Members enable push per browser profile from the notification bell. Unsubscribing
  or signing out disables the server-side subscription.

## 3. Android FCM (Firebase Admin, HTTP v1)

1. In the Firebase console, confirm the project used by the association and that
   Cloud Messaging API (V1) is enabled.
2. Register the Android application with package identity
   `org.combissportverein.kairo` (never change it between releases).
3. Download `google-services.json` and place it at
   `apps/flutter_kairo/android/app/google-services.json`. It is git-ignored and must
   never be committed.
4. Create a service account with the Firebase Messaging role, download the JSON key,
   and place it outside Git, for example `services/api/.private/firebase-admin.json`.
5. Configure the backend (api + worker):

```dotenv
FIREBASE_MESSAGING_ENABLED=true
FIREBASE_SERVICE_ACCOUNT_PATH=/run/secrets/kairo/firebase-admin.json
```

For Docker, mount the key read-only into api and worker:

```yaml
services:
  api:
    volumes:
      - ./services/api/.private/firebase-admin.json:/run/secrets/kairo/firebase-admin.json:ro
  worker:
    volumes:
      - ./services/api/.private/firebase-admin.json:/run/secrets/kairo/firebase-admin.json:ro
```

- Firebase Admin credentials are server/worker only. They never reach the browser or
  the mobile client.
- Push bodies are always generic. Detailed content is read from the authenticated
  inbox after sign-in.

### 3b. Firebase Web Messaging fallback (optional)

The Vue PWA uses VAPID Web Push by default. Firebase Web Messaging is used only
when VAPID is not configured but the public Firebase Web configuration is present.
These are public client identifiers, never service-account keys:

```dotenv
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_STORAGE_BUCKET=
# Optional Firebase Web Push certificate key; omit to use the project default.
VITE_FIREBASE_VAPID_KEY=
```

- The PWA obtains the token through the canonical Service Worker, so background
  messages and VAPID push share one worker; FCM topics are never used for access
  control.
- Full installation model, token rotation, tenant-switch and deduplication
  rules: `docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`.

## 4. Diagnostics

```bash
npm run notifications:firebase:doctor
npm run notifications:firebase:doctor -- --json
```

The doctor reports, without printing secret values: environment variable presence,
credential file presence, Python packages, the configured project id, and whether the
optional live test is enabled. Nothing is sent unless you explicitly pass `--live`
together with `FIREBASE_TEST_TOKEN`; the doctor is never part of generic CI.

In-product operator view: **Admin → Notifications** shows pipeline health (Web Push
configured, Firebase configured, worker running, pending/failed outbox, disabled
subscriptions, retrying subscriptions) plus the operator channel history.

Metrics (`GET /metrics`): `kairo_notification_outbox_pending`,
`kairo_notification_outbox_failed`, `kairo_notification_outbox_oldest_age_seconds`,
`kairo_push_deliveries_total{channel,outcome}`, `kairo_web_push_success_total`,
`kairo_web_push_failure_total`, `kairo_fcm_success_total`, `kairo_fcm_failure_total`,
`kairo_disabled_web_subscriptions`, `kairo_disabled_fcm_tokens`. Notification
contents are never logged.

## 5. Troubleshooting

| Symptom | Check |
| --- | --- |
| Nothing arrives on Android | `FIREBASE_MESSAGING_ENABLED`/path set on **worker**; service account valid; token registered after opt-in; `/notifications/health` `firebase_configured`. |
| Nothing arrives in the browser | HTTPS origin; `WEB_PUSH_*` set on **worker**; service worker registered; permission granted; `/notifications/health` `web_push_configured`. |
| Outbox grows | Beat/worker alive; `pending_outbox`/`oldest_pending_seconds` in health; failed rows carry only the exception type in `last_error`. |
| Subscription disappeared | Invalid targets (Web Push 404/410, FCM unregistered) are disabled by design; ask the member to re-enable push. |
| Push after sign-out | Expected to stop: sign-out revokes the profile binding. Re-enabling requires a new sign-in. |
| Detail missing on lock screen | By design; open Kairo and read the authenticated inbox. |

## 6. Recovery from provider or worker outages

The inbox is the durable record; push is best-effort. Business operations remain
consistent in every validated outage:

| Outage | Guarantee | Recovery |
| --- | --- | --- |
| Celery/Redis (worker) unavailable | The producer transaction already persisted the authenticated inbox rows inline; pending push-outbox rows wait untouched. | When the worker returns, `notifications.process_user_outbox` drains pending rows. No business action must be repeated. |
| Web Push or Firebase temporarily unavailable | The provider returns `TRANSIENT`; up to three bounded attempts run; the event still completes and the subscription `failure_count` increments. | Next event attempts delivery again; the inbox already shows the notification. |
| Push provider raises an unexpected exception | The outbox contains it as a transient failure; the event completes and no retry loop can wedge the queue. | The inbox row is already durable; investigate the provider library if failures repeat. |
| Invalid target (Web Push 404/410, FCM unregistered) | The subscription is disabled by design instead of retrying forever. | The member re-enables push from the inbox; a new subscription row is created. |

Validated by `services/api/tests/test_notification_convergence.py`:
`test_push_provider_outage_keeps_the_inbox_and_contains_the_failure`,
`test_unexpected_provider_exception_is_contained_as_a_transient_failure`, and
`test_worker_outage_defers_delivery_but_preserves_business_state`.

## 7. Physical-device validation checklist

1. Sign in on a physical Android device with the production APK.
2. Grant notification permission from the inbox screen.
3. Confirm `/notifications/health` shows `firebase_configured: true` and pending
   counts draining.
4. Trigger a notification (for example, publish an announcement).
5. Verify: foreground app receives no raw content; background/cold-start shows the
   generic body; tapping opens the authenticated destination after sign-in.
6. Sign out and confirm a new push is not delivered to that installation.
7. Re-sign-in and confirm push is re-enabled automatically after the next opt-in.

## 8. Secret hygiene

- Never commit: `google-services.json`, Firebase Admin service account JSON, VAPID
  private key, FCM credentials, tokens.
- Repository guards: `node scripts/check-sensitive-files.mjs` and the gitleaks
  history scan. `.gitignore` covers `services/api/.private/` and the Flutter Android
  credential paths.
