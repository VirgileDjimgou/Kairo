# Kairo — Current Architecture Snapshot

Last verified: 2026-10-03 (Roadmap V2 Sprint 122)

This file is the concise description of what Kairo IS today. When code and this
file disagree, trust the code and update this file. Historical narrative lives in
`IMPLEMENTATION_ROADMAP.md` and `PROJECT_STATUS.md`; active execution lives in
`docs/roadmap/KAIRO_V2_ROADMAP.json`.

## Shape

Kairo is a **modular monolith** (see ADR-001): one FastAPI application, one
PostgreSQL database, one Celery worker, shared Redis/MinIO/Qdrant. There are no
microservices and no message broker beyond the existing Redis-backed Celery
queue, the PostgreSQL domain-event outbox and the notification outbox.

```
Vue 3 PWA (apps/web)          Flutter client (apps/flutter_kairo)
   |   canonical client                    |  FROZEN legacy/reference (ADR-014)
   |   consumes API contracts only         |  no new business features
   +-------------------+------------------+
                        v
         FastAPI modular monolith (services/api/app)
         core/ identity/ tenancy/ membership/ contributions/
         governance/ disciplinary/ events/ announcements/ documents/
         notifications/ audit/ chat/ rag/ backup/ worker/
                        |
      +---------+-------+--------+-----------+
      v         v       v        v           v
  PostgreSQL   Redis   MinIO   Qdrant   Ollama/Qdrant (optional private AI)
              Celery   objects  vectors
```

## Load-bearing boundaries

- **Backend is the only policy enforcement point** (ADR-002). Roles,
  capabilities, tenant isolation and module entitlements are enforced in FastAPI
  dependencies and services. The frontend only shapes presentation.
- **Every tenant-scoped query includes `tenant_id`.** Cross-tenant reads are
  treated as security defects.
- **RAG authorization happens before prompt assembly** (ADR-003). Retrieved
  chunks are filtered by tenant and access scope before anything reaches the
  LLM; unauthorized chunks are never sent to the model and the LLM never decides
  access.
- **Notifications are delivery hints** (ADR-004, ADR-009, ADR-010). The
  authenticated, tenant-scoped inbox is the source of truth; Web Push (VAPID) and
  Android FCM carry generic bodies only. All producers submit canonical notification
  intents to a policy/recipient-resolver layer; a PostgreSQL-backed outbox feeds the
  inbox and replaceable push providers (`app/providers/push/`), invalid targets are
  disabled, retries are bounded, and sign-out revokes the profile binding.
- **The OpenAPI schema is the committed client boundary** (ADR-011). FastAPI's
  schema is versioned at `docs/api/openapi.json`; CI fails on breaking changes,
  stale generated TypeScript/Dart contract types or client calls that no longer
  map to a documented operation. Generated types coexist with thin hand-written
  gateways and never make authorization decisions.
- **Modules compose through an internal registry** (ADR-013). Each module package
  ships a `module.py` descriptor (capabilities, dependencies, routers, search/AI
  hooks, health hook, domain events, navigation); `app/main.py`, module toggles,
  search and chat consume the registry instead of importing modules directly.
  Discovery is repository-internal — no untrusted plugin execution. Navigation
  metadata is served tenant/capability-filtered by `GET /api/v1/modules`.
- **Operational health is layered and privacy-safe** (ADR-012). `/health` returns
  dependency, backup and outbox-pipeline status with counts only; `/health/live`
  and `/health/ready` serve orchestration probes; `/metrics` carries outbox and
  backup gauges without tenant/member/token labels; worker logs bind task and
  request correlation ids.
- **Operational documents never enter Git** (ADR-007). Association documents
  live in MinIO/S3 through the document module.

## Identity and tenancy

- JWT access tokens bound to a tenant; refresh validated against persistent
  sessions; MFA (TOTP); invitations; assisted one-time recovery passwords;
  session inventory and revocation. The identity module is decomposed into
  domain packages (`authentication`, `passwords`, `sessions`, `mfa`,
  `invitations`, `recovery`, `administration`, `tenancy`) composed behind the
  unchanged `AuthService` facade, with shared repository/request-context state
  in `base.py`. (`services/api/app/modules/identity/`)
- Tenant membership resolution, branding and module toggles per tenant.
  (`services/api/app/modules/tenancy/`)
- Canonical office roles: member, secretary_general, treasurer, auditor, censor,
  sports_manager, president, vice_president, principal_admin (+ legacy `admin`).
- Roles are capability bundles. Effective capabilities are exposed read-only on
  `GET /auth/me` (active tenant) and on each tenant membership, and the clients
  use them for navigation and action visibility. Backend enforcement still
  checks the specific capability per endpoint; presentation-scoped capabilities
  never gate an authorization decision (ADR-008).

## Business modules

| Domain | Backend module | Notes |
| --- | --- | --- |
| Members | `membership/` | profiles, lifecycle, statement |
| Finance | `contributions/` (models, schemas, repository, router) + `finance/` (bounded context) | contributions, payments, receipts + custody handover, expenses, budgets, exports, reminders. `finance/` holds the decomposed domains (`contributions`, `receipts`, `custody`, `expenses`, `budgeting`, `reminders`, `reporting`), a notification contract seam (`notifications.py`) and a `ContributionService` facade; `contributions/service.py` re-exports the facade for API compatibility. Each command keeps its own transaction. |
| Governance | `disciplinary/`, `events/`, `announcements/`, policies | role-scoped visibility |
| Knowledge | `documents/`, `rag/`, `chat/` | ingestion, citations, refusal behavior. `chat/contexts/` holds the authorized domain context provider registry (membership, finance, governance, documents/publication, disciplinary, events/sports); providers check the capability-derived domain policy before querying, and `ChatService` consumes only the registry plus permission-aware RAG retrieval. |
| Operations | `audit/`, `backup/`, `notifications/`, `domain_events/`, `module_registry/`, `worker/` | journal, encrypted backups, outbox delivery. `notifications/` is decomposed into `inbox`, `policy`, `preferences`, `devices`, `health`, `outbox` (user-facing) and `history`, `reconciliation`, `dispatch` (operator-facing), composed behind the unchanged `UserNotificationService` and `NotificationService` facades. `domain_events/` holds the internal event log, consumer registry and outbox service; `audit/event_handlers.py` and `notifications/event_handlers.py` consume events without business modules importing transport code. Push transports are provider protocols under `app/providers/push/` (Web Push VAPID + Firebase Admin FCM) with deterministic fakes for tests. Browser/Android installations are normalized in `notification_devices` (platform, browser, bounded metadata, status, timestamps) with provider subscriptions in `web_push_subscriptions`/`firebase_push_subscriptions`; delivery is deduplicated per `(recipient, installation)` (`docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`). Notification targets are normalized by a boundary-aware internal allowlist (`deep_links.py`, ADR-015); the outbox carries a versioned canonical envelope and clients fall back to the authenticated inbox for unsafe or inaccessible targets. `module_registry/` discovers per-module descriptors and composes routers, toggles, search/AI hooks, health checks and navigation (`GET /api/v1/modules`). |

## Clients

- **Vue 3 PWA** (`apps/web`) — canonical supported client (ADR-014). Pinia
  stores, vue-router, typed API gateways under `src/api/`, shared capability
  constants under `src/config/capabilities.ts`, and domain feature modules under
  `src/features/` (`finance`, `dashboard`, `members`, `attention`, `search`).
  Router views are thin containers that orchestrate feature components and
  composables; navigation and action visibility follow API capabilities, and no
  authorization decision is made in the client. Notification inbox/push/health
  DTOs come from the generated OpenAPI contract types
  (`src/api/generated/contracts.ts`). A single canonical Service Worker
  (`src/sw.ts`, vite-plugin-pwa `injectManifest`) owns install/activate, the
  offline strategy, update detection, Web Push display, Firebase background
  messages and notification-click routing. Notification clicks focus an existing
  window and post a `kairo:navigate` message; the client validates the target
  against the router, authentication state, role/module metadata and tenant
  toggles and opens the exact authorized route, falling back to the
  authenticated inbox for unsafe, unknown, redirected or inaccessible targets.
  See `docs/pwa/PWA_ARCHITECTURE.md` and ADR-015.
- **Flutter client** (`apps/flutter_kairo/`) — **FROZEN / LEGACY REFERENCE**
  (ADR-014). It consumes the same API contracts and makes no local authorization
  decisions, but receives no new business features and is not a blocking job of
  the default release pipeline. Its source tree is preserved for behavior,
  notification and parity reference; Flutter-only capability continuity and the
  S120–S124 notification/deep-link gaps are tracked in
  `docs/pwa/FLUTTER_TO_PWA_PARITY.md`. Typed OpenAPI contract classes remain in
  `lib/core/api/generated/contracts.dart` and are still drift-checked by the
  SDK-free contract job.

## Runtime and deployment

- Docker Compose stack (api, worker, web, postgres, redis, minio, qdrant,
  ollama, cloudflared); production override `docker-compose.prod.yml` fails
  closed on missing secrets.
- Cloudflare Tunnel ingress; Nginx serves the built PWA and proxies `/api/`.
- Encrypted, signed PostgreSQL/MinIO backup archives with restore drills.

## Quality gates

Backend `ruff` + `mypy` (303 source files) + `pytest` (394 tests), Web `vue-tsc` + `vite build` +
four Playwright packs (locale, roles, release-candidate, accessibility) plus the
PWA packs (navigation contract on the dev server; single-worker/offline on the
built preview) and the notification-installation pack, the canonical Service
Worker guard (`node scripts/check-pwa-service-worker.mjs`), OpenAPI contract
checks (`scripts/check-openapi-contract.mjs`, generated-contract drift check,
client route coverage), an opt-in performance regression check
(`npm run perf:check`, statement counts deterministic), repository guards
(`check-sensitive-files`, `check-i18n-coverage`, `check-api-collection-paths`)
and gitleaks history scan. Flutter `analyze`/`test`/builds are **optional and
manual** since Sprint 119 (`.github/workflows/flutter-legacy.yml`, ADR-014) and
never block the release pipeline. Commands of record:
`docs/operations/validation-baseline.md`.

## Known structural debt (tracked in Roadmap V2)

- Remaining structural debt: monolithic `messages.ts`; large admin views
  (`AdminDocumentsView.vue`, `AdminNotificationsView.vue`).
- Sprint 110 decomposed the 1174-line `contributions/service.py` into the
  `app/modules/finance/` bounded context (largest domain file 349 lines, public
  facade 29 lines) without changing API contracts or finance semantics; report
  generation and notification triggering are separated behind domain modules
  and a notification contract seam.
- Sprint 111 decomposed the 1834-line `identity/service.py` (44 methods) into
  eight identity domain packages behind a 25-line `AuthService` facade, and
  split the notification services into user-facing (inbox, preferences,
  devices, outbox) and operator-facing (history, reconciliation, dispatch)
  domains; API contracts, MFA/session security and push/FCM registration are
  unchanged (317 backend tests pass).
- Sprint 112 removed `ChatService` as a domain coupling hub: structured context
  now comes from the `chat/contexts/` provider registry (six authorized domain
  providers), shrinking `chat/service.py` from 1243 to 720 lines while keeping
  retrieval filtering, refusal behaviour and prompt-injection protections
  unchanged (322 backend tests pass).
- Sprint 113 decoupled the receipt lifecycle from secondary effects: the finance
  receipt/custody commands publish internal domain events to the PostgreSQL-backed
  `domain_events` outbox, and audit projection, inbox notification enqueueing and
  custody email notices consume them through a registered handler registry. Audit
  and notification projection are idempotent by event/deduplication key, retries are
  safe, and no event handler mutates money (327 backend tests pass).
- Sprint 114 converged the notification platform: one policy/recipient-resolver
  pipeline writes the canonical envelope (event id, correlation id, push policy),
  push transports are replaceable providers with deterministic fakes, invalid
  Web Push/FCM targets are disabled, transient failures retry with bounded backoff,
  sign-out revokes the device profile binding, deep links are allowlisted and
  resolved against the authenticated routers, `/metrics` and
  `GET /notifications/health` expose pipeline state, and the Vue admin console
  renders notification health (337 backend tests, 48 Flutter tests pass).
- Sprint 115 made FastAPI's OpenAPI schema the committed client boundary: the
  schema is versioned at `docs/api/openapi.json`, CI fails on breaking changes,
  generated TypeScript and Dart contract types are drift-checked, every literal
  client call is verified against a documented operation, and the client feature
  parity matrix lives in `docs/api/CLIENT_FEATURE_PARITY.md` (337 backend tests,
  50 Flutter tests pass).
- Sprint 116 made Kairo operationally diagnosable and measurable: `/health` now
  covers backup and both outboxes with counts only, `/health/live` and
  `/health/ready` serve orchestration probes, `/metrics` gained outbox/backup
  gauges plus Grafana panels, Celery tasks carry request correlation into
  structured worker logs, a committed 200/1000-member performance baseline with
  p50/p95 and statement counts lives under `docs/performance/`, and the first
  N+1 offenders (managed-user directory, unreachable notifications, batch
  reminders, member statements) are batched with regression tests (346 backend
  tests pass).
- Sprint 117 added the internal module registry: every module ships a `module.py`
  descriptor and central composition (routers, tenant toggles, search providers,
  optional AI context providers, health hooks, navigation metadata) consumes the
  registry; validation rejects duplicate keys, unknown/cyclic dependencies and
  unknown capabilities; `GET /api/v1/modules` serves tenant/capability-filtered
  navigation metadata; tenant-specific role bundles store validated canonical
  capabilities (migration 0033) and merge into effective capabilities; a minimal
  sample module proves automatic discovery (359 backend tests pass).
- Sprint 107 decomposed the finance, dashboard and member-admin mega-views into
  `src/features/` modules (finance workspace 1252 → 216 lines, dashboard
  823 → 104, member admin 771 → 170) without changing behavior or moving
  authorization into the frontend.
- Sprint 118 produced the release candidate: fresh-image dependency pinning,
  the 0029 → 0033 upgrade with a pre-migration safety backup, encrypted-archive
  restore and rollback drills, notification outage recovery tests, and a WCAG
  2.2 AA accessibility pass.
- Sprint 119 consolidated the client surface: the Vue 3 PWA is the canonical
  client and Flutter is frozen as legacy/reference code (ADR-014), Flutter
  analyze/test/builds moved to the manual `flutter-legacy` workflow so they can
  no longer block `main`, and Flutter-only capability continuity plus the
  S120–S124 notification/deep-link gaps are recorded in
  `docs/pwa/FLUTTER_TO_PWA_PARITY.md`.
- Sprint 120 unified the PWA Service Worker: one canonical worker handles
  lifecycle, offline strategy, update detection, VAPID Web Push, Firebase
  background messages and notification clicks; clicks focus an existing window
  and post a `kairo:navigate` message that Vue Router resolves to the exact
  authorized route (with `/login?redirect=` preservation for unauthenticated
  users); a static guard and built-worker Playwright tests prove a single
  controlling worker and the offline fallback. See `docs/pwa/PWA_ARCHITECTURE.md`.
- Sprint 121 normalized the browser notification installation model (migration
  0034): devices carry platform, browser, bounded metadata, status and
  last-seen/updated/revoked timestamps; provider subscriptions record their
  provider. VAPID Web Push stays the default browser transport and Firebase Web
  Messaging is the configured fallback; delivery is deduplicated per
  `(recipient, installation)`, FCM token rotation disables obsolete tokens,
  tenant switching revokes the previous tenant binding first, and notification
  health reports retrying subscriptions. See
  `docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`.
- Sprint 122 secured notification deep links: a boundary-aware backend allowlist
  normalizes every target (unknown/external values become `/notifications`), the
  outbox payload carries `envelope_version: 1`, the PWA re-validates targets
  against the actual router, authentication state, role/module metadata and
  tenant toggles, and unsafe/unknown/redirected/inaccessible targets fall back
  to the authenticated inbox instead of the dashboard; representative business
  cases prove generic push payloads and exact targets (ADR-015).
- Status: sprints 108–122 addressed i18n, capabilities, service decomposition,
  domain events, notification convergence, the contract boundary, operational
  health/performance, the module framework, release hardening, the PWA-first
  client consolidation, the unified PWA Service Worker, the normalized
  notification installation model and secure actionable deep links; the active
  program is S119–S128 (PWA-first, white-label SaaS).
