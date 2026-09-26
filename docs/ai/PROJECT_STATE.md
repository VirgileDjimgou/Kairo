# Project State

Last verified: 2026-09-25 (Roadmap V2 Sprint 102)

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

- Verified baseline (2026-09-25): 303 backend tests, web type-check/build, three
  Playwright packs (locale 20, roles 17, release-candidate 9), Flutter analyze +
  46 tests + web/Android builds, repository guards green. Details:
  `docs/operations/validation-baseline.md`.
- Open security item (HUMAN_REQUIRED): historical JWT secret rotation and
  history remediation — `docs/security/HISTORY_EXPOSURE_REPORT.md`.
- Structural debt (oversized services/views, inline locale copy) is being paid
  down by Roadmap V2 sprints 107–113. Sprint 107 extracted the finance,
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
