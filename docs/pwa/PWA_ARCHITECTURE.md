# Kairo PWA Architecture

Status: Active — Roadmap V2 Sprint 120
Decision records: ADR-010 (unified notification pipeline), ADR-014 (PWA-first)

The Vue 3 PWA (`apps/web/`) is the canonical client. This document describes its
Service Worker, install, update and notification-navigation architecture.

## One canonical Service Worker

- Built with Vue 3 + Vite + `vite-plugin-pwa` using `strategies: 'injectManifest'`
  and a single custom worker source: `apps/web/src/sw.ts` (configured in
  `apps/web/vite.config.ts`).
- The worker is emitted as `/sw.js` and registered once through
  `virtual:pwa-register` in `apps/web/src/main.ts`. `web-push.ts` only reuses the
  same registration (`navigator.serviceWorker.getRegistration('/')`).
- No second worker file exists. A Firebase `firebase-messaging-sw.js` is
  deliberately avoided: FCM background handling is registered inside the same
  canonical worker, so push and notification-click behavior cannot be split
  between competing registrations.
- `node scripts/check-pwa-service-worker.mjs` (`npm run pwa:check`) enforces this
  invariant and the required worker contracts in CI.

## Lifecycle, offline and updates

- `self.skipWaiting()` + `clientsClaim()` activate the current worker
  immediately; `cleanupOutdatedCaches()` removes stale precaches.
- `precacheAndRoute` caches every hashed asset from the build manifest but never
  `index.html`: a cache-first HTML shell can pin an obsolete bundle and obsolete
  API URLs.
- Navigations use `NetworkFirst` (`kairo-pages`, 5 s network timeout): online
  users always receive the current HTML entrypoint; the cached response is the
  offline fallback.
- Update detection is handled in `main.ts` (`onNeedRefresh` →
  `kairo:pwa-update-available` event → notice UI → apply after 5 s or on user
  action) plus a 60 s update poll.

## Notification navigation contract

```text
push / FCM background message
        |
        v
Service Worker shows a notification with a safe internal target
        |
        v
notificationclick
        |
        +-- existing window?  clients.matchAll() -> client.focus()
        |                     -> postMessage({ type: 'kairo:navigate', target })
        |                          -> Vue Router push (exact authorized route)
        |
        +-- no window?        clients.openWindow(target)
```

- Targets are backend-owned safe internal paths. `safeTarget()` in the worker
  rejects anything that is not a same-origin absolute path and falls back to
  `/dashboard`; `safeInternalTarget()` in
  `apps/web/src/services/pwa-navigation.ts` repeats the validation on the client.
- The client never trusts the payload for authorization: the Vue Router guard
  re-checks authentication, role and module state, and the backend authorizes
  every request. An unauthenticated target becomes
  `/login?redirect=<target>` so the exact destination survives sign-in.
- This is navigation safety, not access control; no notification payload can
  navigate to an external URL.

## Push transports

- **Web Push (VAPID)** is the standards-based default transport for browsers,
  owned by the PWA. The outbox provider sends a generic body and a safe target
  only.
- **Firebase Cloud Messaging** is handled in the same worker through
  `firebase/messaging/sw` `onBackgroundMessage`. It is used as the browser
  transport when VAPID is not configured but the public Firebase Web
  configuration is present (`VITE_FIREBASE_*`); when neither is configured, the
  enable action reports `not_configured`. FCM-shaped push events are delegated
  to the Firebase handler so a message is never displayed twice.
- Installation registration (`POST /notifications/devices` and the provider
  endpoints) sends normalized browser metadata and a random installation
  identity; one installation always resolves to one delivery provider per
  recipient, and the outbox skips a Firebase send when the same
  `(recipient, installation)` pair was already delivered through Web Push.
- Detailed notification content is never placed in a push payload; the
  authenticated inbox remains the source of truth. Full model and lifecycle:
  `docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`.

## Verification

```bash
node scripts/check-pwa-service-worker.mjs   # architecture guard (CI)
cd apps/web && npm run test:e2e:pwa         # navigation contract (dev server)
cd apps/web && npm run test:e2e:pwa:built   # single worker + offline (vite preview)
```

The built pack proves that exactly one Service Worker controls the origin, that
the web manifest is installable, and that an offline navigation falls back to
the cached shell. Manual real-device validation (Android Chrome, installed PWA,
background/closed delivery) remains part of the S128 pilot checklist.
