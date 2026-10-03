# Project State

Last verified: 2026-10-03 (Roadmap V2 Sprint 122)

## What this file is

A short orientation for AI agents and humans. It deliberately does NOT track
sprint status: that lives only in `docs/roadmap/KAIRO_V2_ROADMAP.json` and the
batch state machine (`.kairo/sprint-batch/`, untracked).

## Product snapshot

Kairo is a multi-tenant association-management platform: role-aware workspaces
(membership, finance with receipt custody, governance, discipline, documents,
events, announcements), a secure citation-based private assistant, an
authenticated notification inbox with Web Push and Android FCM delivery, audit
journaling and encrypted backup/recovery. The Vue 3 PWA is the canonical,
supported client (ADR-014); the Flutter client (Android + Flutter Web) is frozen
as legacy/reference code, consumes the same FastAPI contracts, and receives no
new business features during S119–S128.

## Where truth lives

| Question | Source |
| --- | --- |
| What is the product today? | `docs/architecture/CURRENT_ARCHITECTURE.md` |
| Which decisions are binding? | `docs/architecture/decisions/` |
| What is the active sprint? | `docs/roadmap/KAIRO_V2_ROADMAP.json` + `npm run sprint:batch:status` |
| What was delivered historically? | `IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md` (historical sections) |
| How do I run the gates? | `docs/operations/validation-baseline.md` |
| What are the hard rules? | `AGENTS.md`, `constitution/KAIRO_CONSTITUTION.md` |
| Product strengths and delivery narrative? | `PROJECT_STATUS.md` |

## Current engineering posture

- Verified baseline (2026-10-03): 394 backend tests, web type-check/build, four
  Playwright packs (locale 20, roles 17, release-candidate 9, accessibility 6)
  plus the PWA and notification-installation packs, OpenAPI contract checks, an
  opt-in performance regression check, repository guards green. Flutter
  analyze/tests/builds are optional and manual since Sprint 119
  (`.github/workflows/flutter-legacy.yml`, ADR-014). Details:
  `docs/operations/validation-baseline.md`. Sprint 118 evidence:
  `docs/sprint-118-release-candidate-evidence.md`.
- Open security item (HUMAN_REQUIRED): historical JWT secret rotation and
  history remediation — `docs/security/HISTORY_EXPOSURE_REPORT.md`.
- Structural debt (oversized services/views, inline locale copy) is being paid
  down by Roadmap V2 sprints 107–118. Sprint 107 extracted the finance,
  dashboard and member-admin mega-views into `apps/web/src/features/` modules
  with unchanged behavior and green web gates. Sprint 108 split the monolithic
  i18n catalog into 11 feature catalogs per locale (873 keys, exact FR/EN/DE
  parity enforced by `check-i18n-parity.mjs`) and removed the dashboard/finance
  locale ternaries; a shrinking set of inline ternaries remains in other views
  and composables and is tracked for follow-up. Sprint 109 exposed effective
  capabilities on `/auth/me` and tenant memberships (ADR-008); the web client
  now derives navigation and action visibility from capabilities, with a
  drift-checked role-bundle fallback only for payloads that omit the field.
  Sprint 110 split the finance service into the `app/modules/finance/` bounded
  context (contributions, receipts, custody, expenses, budgeting, reminders,
  reporting) with an unchanged public facade and a dedicated
  `test_finance_workflows.py` regression suite; 317 backend tests pass.
  Sprint 111 decomposed `identity/service.py` (1834 lines) into eight identity
  domain packages behind an unchanged `AuthService` facade and split the
  notification services into inbox/preferences/devices/outbox plus
  history/reconciliation/dispatch domains; API contracts, MFA/session security,
  Web Push and FCM registration behaviour are unchanged.
  Sprint 112 replaced the chat service's direct domain coupling with an
  authorized context provider registry (`chat/contexts/`, six domain
  providers); retrieval filtering and prompt-injection protections are
  unchanged and the backend suite now has 322 passing tests.
  Sprint 113 added the internal domain-event outbox
  (`app/modules/domain_events/`): receipt declaration, validation, handover and
  custody commands publish events instead of importing audit/notification code,
  consumers are registered per module, audit and inbox projection are idempotent
  by deduplication key, and the Celery task `domain_events.process_outbox`
  retries pending events safely; the backend suite now has 327 passing tests.
  Sprint 114 converged notifications on that foundation: a single policy/recipient
  resolver writes the canonical envelope, push transports are provider protocols
  with fakes, invalid Web Push/FCM targets are disabled, retries are bounded,
  sign-out revokes the profile binding, deep links are allowlisted, notification
  metrics and `GET /notifications/health` are observable, and the Vue admin
  console renders pipeline health; the backend suite has 337 passing tests and
  the Flutter suite 48, with the event matrix and operator guide under
  `docs/notifications/`.
  Sprint 115 made the OpenAPI schema the committed client contract boundary:
  `docs/api/openapi.json` is versioned and regenerated deterministically, CI
  detects breaking API changes, generated TypeScript/Dart contract types are
  drift-checked, literal client calls must map to documented operations, and
  `docs/api/CLIENT_FEATURE_PARITY.md` records the Vue/Flutter feature matrix;
  the Flutter suite now has 50 passing tests (including generated-contract
  parity).
  Sprint 116 hardened observability and performance: `/health` reports backup,
  notification-outbox and domain-event-outbox status with counts only,
  `/health/live` and `/health/ready` serve orchestration probes, `/metrics`
  carries outbox/backup gauges (Grafana panels included), Celery tasks bind
  request correlation into structured worker logs, a committed 200/1000-member
  performance baseline (`docs/performance/`) records p50/p95 and SQL statement
  counts with `npm run perf:check`, and the first N+1 paths are batched with
  regression tests; the backend suite has 346 passing tests.
  Sprint 117 made modules extensible through an internal registry: each module
  package ships a `module.py` descriptor and central composition (routers,
  tenant toggles, search providers, optional AI context providers, health hooks,
  navigation) consumes the registry; validation catches duplicate keys,
  unknown/cyclic dependencies and capability typos; `GET /api/v1/modules` serves
  tenant/capability-filtered navigation metadata; tenant-specific role bundles
  store validated canonical capabilities (migration 0033) and are merged into
  effective JWT/`/auth/me` capabilities; a minimal sample module demonstrates
  automatic discovery; the backend suite has 359 passing tests.
  Sprint 118 produced the release candidate: a fresh-image startup blocker was
  fixed (`sqlalchemy[asyncio]>=2.0.36,<2.1.0` guarantees `greenlet`), the
  deployed schema upgraded 0029 → 0033 with a pre-migration safety backup and
  preserved data, encrypted-archive restore and pre-upgrade rollback drills
  passed in isolated containers, notification recovery for Celery/Web Push/
  Firebase outages gained regression tests, and a WCAG 2.2 AA audit added a
  localized skip link, named progress bars and app-wide contrast fixes; the
  backend suite has 362 passing tests.
  Sprint 119 consolidated the client surface: the Vue 3 PWA is the canonical
  client, Flutter is frozen as legacy/reference code (ADR-014), the blocking CI
  pipeline no longer runs Flutter, and Flutter-only capability continuity plus
  the S120–S124 notification/deep-link gaps are recorded in
  `docs/pwa/FLUTTER_TO_PWA_PARITY.md`.
  Sprint 120 unified the PWA Service Worker: one canonical worker
  (`apps/web/src/sw.ts`) owns lifecycle, offline strategy, update detection,
  VAPID Web Push, Firebase background messages and notification clicks; clicks
  focus an existing window and post a `kairo:navigate` message resolved by Vue
  Router to the exact authorized route, with `?redirect=` preservation for
  unauthenticated users. `npm run pwa:check` guards the single-worker contract
  and built-worker Playwright tests prove the single controlling worker and the
  offline fallback; architecture lives in `docs/pwa/PWA_ARCHITECTURE.md`.
  Sprint 121 normalized browser notification installations (platform, browser,
  bounded metadata, status, timestamps, explicit provider; migration 0034),
  kept VAPID Web Push as the default browser transport with Firebase Web
  Messaging as the configured fallback, deduplicated delivery per installation,
  disabled obsolete FCM tokens on rotation, revoked the previous tenant binding
  before tenant switching, exposed retrying subscription counts in notification
  health and added eight backend plus four web installation tests; the backend
  suite has 370 passing tests and the model is documented in
  `docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`.
  Sprint 122 secured notification deep links: a boundary-aware backend allowlist
  normalizes every target (unknown/external values become `/notifications`), the
  outbox payload carries `envelope_version: 1`, the PWA re-validates targets
  against the router, authentication state, role/module metadata and tenant
  toggles with an authenticated-inbox fallback, and representative business
  cases prove generic push payloads and exact targets (ADR-015); the backend
  suite has 394 passing tests.
