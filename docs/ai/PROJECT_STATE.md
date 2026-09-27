# Project State

Last verified: 2026-09-26 (Roadmap V2 Sprint 115)

## What this file is

A short orientation for AI agents and humans. It deliberately does NOT track
sprint status: that lives only in `docs/roadmap/KAIRO_V2_ROADMAP.json` and the
batch state machine (`.kairo/sprint-batch/`, untracked).

## Product snapshot

Kairo is a multi-tenant association-management platform: role-aware workspaces
(membership, finance with receipt custody, governance, discipline, documents,
events, announcements), a secure citation-based private assistant, an
authenticated notification inbox with Web Push and Android FCM delivery, audit
journaling and encrypted backup/recovery. The Vue 3 PWA is the production
client; a parallel Flutter client (Android + Flutter Web) consumes the same
FastAPI contracts.

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

- Verified baseline (2026-09-26): 337 backend tests, web type-check/build, three
  Playwright packs (locale 20, roles 17, release-candidate 9), Flutter analyze +
  50 tests + web/Android builds, OpenAPI contract checks, repository guards
  green. Details: `docs/operations/validation-baseline.md`.
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
