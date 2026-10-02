# ADR-014: PWA-First Client Consolidation, Flutter Frozen As Legacy Reference

Status: Accepted (supersedes ADR-006 for client ownership and release targets)

## Context

ADR-006 introduced the Flutter client (`apps/flutter_kairo/`) as a separate
application with Android and Flutter Web as first release targets, while keeping
the Vue 3 PWA in production. Flutter sprints F0–F9 delivered a large,
feature-parity client with native Android capabilities (FCM, sharing, secure
storage, offline drafts) and its own release tooling.

By the start of Roadmap V2's S119–S128 program, this created three problems:

1. **Two clients, one product.** Every backend contract change, notification
   change and release gate had to keep Flutter green, even though the Vue 3 PWA
   is the client the association actually runs.
2. **Blocking CI.** The default `CI` workflow ran Flutter analyze, format, tests
   and two builds on every push and pull request. A Flutter-only failure made
   `main` red even when the PWA and API were healthy.
3. **Unclear ownership.** The roadmap, `PROJECT_STATUS.md`, `docs/flutter/` and
   `AGENTS.md` described Flutter as an active parallel track, so agents could
   legitimately start new Flutter business work while S119–S128 planned PWA
   capabilities (Service Worker, Web Push/FCM installations, deep links,
   white-label branding) that would duplicate it.

The product decision is to consolidate on the PWA as the canonical client.

## Decision

- **The Vue 3 PWA (`apps/web/`) is the canonical, supported Kairo client.**
  All new product capability during S119–S128 is delivered there.
- **The Flutter client (`apps/flutter_kairo/`) is FROZEN as legacy/reference
  code.** It receives no new business features, is not a blocking job of the
  default release pipeline, and must not replace, weaken or silently change the
  PWA. Its source tree is preserved for behavior, notification and parity
  reference.
- **The Flutter track roadmap is closed.** Flutter sprints F0–F9 are historical.
  `docs/flutter/FLUTTER_APP_ROADMAP.md`, `docs/flutter/PROJECT_STATUS.md`,
  `docs/flutter/FEATURE_PARITY.md`, `apps/flutter_kairo/AGENTS.md` and
  `prompts/FLUTTER_CONTINUE_UNIVERSAL.md` are marked as frozen reference.
- **CI:** Flutter analyze/test/build move out of the default blocking `CI`
  workflow into a separate manual `flutter-legacy` workflow
  (`workflow_dispatch`). The release pipeline is: Security, API, Contracts,
  Web, Production. A Flutter failure can no longer make `main` red.
- **Capability continuity:** Flutter-only capabilities are inventoried in
  `docs/pwa/FLUTTER_TO_PWA_PARITY.md` and each is classified as already
  available in the PWA, planned for S120–S124, or explicitly deprecated. The
  notification/deep-link gaps that S120–S124 must close are recorded in the
  same document.
- **No deletion.** Flutter archival or removal is a separate explicit decision
  after S128 (see the Flutter Exit Condition in the Roadmap V2 document), never
  part of S119–S128.

## Consequences

- The backend, the PWA and the API contract remain the only release-critical
  artifacts; Flutter checks are opt-in and can be run manually when reference
  behavior must be consulted.
- Generated Dart contract types and the Flutter route-coverage scan remain in
  the contract job as deterministic, SDK-free drift checks (they do not run
  Flutter), so the API boundary cannot drift unnoticed while the client is
  frozen. S127 may reassess this.
- Flutter Web staging (`docker-compose.flutter-web.yml`, the Flutter Nginx
  gateway and `docs/flutter/RELEASE_RUNBOOK.md`) is preserved but is not part of
  the PWA release path and receives no production promotion.
- Flutter-only capabilities that the PWA does not yet have become explicit
  S120–S124 work items instead of accidental parity debt.
- ADR-006 remains historically relevant for how the Flutter client was built;
  this ADR supersedes its active roadmap ownership and release-target claims.
