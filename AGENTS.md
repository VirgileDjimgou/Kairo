# Kairo Agent Guide

This repository is designed to be continued from multiple agentic IDEs, including Codex, Cursor, and GitHub Copilot.

## Purpose

Use this file as the universal entry point before implementing or reviewing anything.

## Active Roadmap And Autopilot Aliases

Roadmap V2 (`docs/roadmap/KAIRO_V2_ROADMAP.md` and
`docs/roadmap/KAIRO_V2_ROADMAP.json`) is the canonical active execution roadmap.
`IMPLEMENTATION_ROADMAP.md` is the historical Sprint 0–99 record. Execution policy
lives in `docs/automation/SPRINT_BATCH_AUTOPILOT.md`.

Interpret these operator phrases exactly:

- **Start Next Sprint** → execute exactly ONE next unfinished Roadmap V2 sprint.
- **Start Next Sprints N** → execute `N` consecutive Roadmap V2 sprints, one at a
  time, with hard quality gates between sprints. Default `N = 1`; allowed
  `1 <= N <= 10`; hard maximum 10 per autonomous batch. If `N > 10`, cap at 10 and
  report the cap.
- **Start Next Sprints Resume** → resume the incomplete batch from its real state
  (never repeat a completed sprint, never restart a partially implemented sprint
  from scratch without inspecting it first).

Equivalent entry points: `/start-next-sprint`, `/start-next-sprints N`,
`/sprint-batch-status`, `/sprint-batch-resume`, `/sprint-batch-stop`, and the
`npm run sprint:batch:*` commands.

Runtime batch state lives in `.kairo/sprint-batch/` and is untracked. The machine
roadmap is tracked. During a batch, record sprint transitions through
`scripts/sprint-batch/cli.mjs` (`begin`, `verify`, `evaluate`, `complete`, `block`,
`fail`) so the state machine stays the source of truth.

## Read Order

Read these files in this order at the beginning of every new session:

1. `README.md`
2. `AGENTS.md`
3. `constitution/KAIRO_CONSTITUTION.md`
4. `docs/roadmap/KAIRO_V2_ROADMAP.md` (active execution roadmap)
5. `docs/automation/SPRINT_BATCH_AUTOPILOT.md` (execution policy)
6. `docs/architecture/CURRENT_ARCHITECTURE.md` and `docs/architecture/decisions/`
7. `PROJECT_STATUS.md` (product state)
8. `docs/ai/PROJECT_STATE.md` and `docs/ai/NEXT_SPRINT.md` (if present)
9. `prompts/KAIRO_SPRINT_EXECUTOR.md` and `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md`
10. `IMPLEMENTATION_ROADMAP.md` (historical Sprint 0–99 record only)
11. `prompts/CODEX_AUTOPILOT.md`
12. `orgmind_prompt_pack/01_PROJECT_CONSTITUTION.md`
13. `orgmind_prompt_pack/02_ARCHITECTURE.md`
14. `orgmind_prompt_pack/03_ROADMAP_SPRINTS.md`
15. `orgmind_prompt_pack/09_SECURITY_AND_LLM_SAFETY.md`

If architecture or behavior is unclear, inspect the code before making assumptions.

## Conflict Resolution

If two sources disagree, use this order:

1. Verified code and tests
2. `PROJECT_STATUS.md`
3. `docs/roadmap/KAIRO_V2_ROADMAP.json` (active sprint state and acceptance)
4. `constitution/KAIRO_CONSTITUTION.md`
5. `orgmind_prompt_pack/`
6. `IMPLEMENTATION_ROADMAP.md` (historical record only)
7. `README.md`

If code and docs diverge, trust verified code first, then update the docs you touched.

## Non-Negotiable Rules

- Never hardcode COMBIS as product logic. It is a demo tenant only.
- Every tenant-scoped query must include `tenant_id`.
- The backend is the only policy enforcement point.
- The LLM never decides access control.
- Retrieval filtering must happen before prompt assembly.
- Never send unauthorized chunks to the LLM.
- Frontend code must consume API contracts only.
- Preserve the modular monolith structure unless a documented ADR justifies change.
- Update tests and documentation when behavior changes.
- Use English for code, identifiers, comments, tests, and file names.

## Sprint Continuity Workflow

For every new coding session:

1. Run `git status --short` and preserve unrelated user changes.
2. Read the files listed in the read order above.
3. Confirm the active sprint from `docs/roadmap/KAIRO_V2_ROADMAP.json` and the batch
   state (`.kairo/sprint-batch/state.json`), using `PROJECT_STATUS.md` for context.
4. Implement only that sprint or an explicitly requested stabilization task.
5. Do not silently skip ahead to later roadmap modules. Dependencies must be
   completed first; a blocked sprint blocks the batch.
6. Run the most relevant tests for the touched area.
7. Record sprint transitions through `scripts/sprint-batch/cli.mjs`; update
   `PROJECT_STATUS.md` when the delivered product state changes.
8. Never weaken a test, tolerance, security check or authorization check to obtain a
   passing gate.

## Expected Engineering Style

- Small vertical slices.
- Explicit naming.
- Thin routers, service orchestration, repository isolation.
- Provider abstractions for external services.
- Typed DTOs at API boundaries.
- No unrelated refactors during sprint work.

## Done Means

A sprint increment is done only when:

- the implementation compiles or builds,
- relevant tests pass,
- tenant isolation is preserved,
- permissions are enforced in the backend,
- docs are updated,
- the feature is demonstrable in the current repo.

## Translation Governance

Kairo uses a French-first, English-second, German-third i18n contract.

- All user-facing strings in Vue templates must use `localeStore.t('key')` or the `t()` helper.
- Never add hardcoded English, French, or German strings directly in templates.
- All new i18n keys must be added to all three locales (`fr`, `en`, `de`) in `apps/web/src/i18n/messages.ts`.
- The `localeStore` is imported from `@/stores/locale.store`.
- Views may use an inline `copy` computed pattern for view-specific strings, but this pattern must switch on `localeStore.currentLocale` and cover all three locales.
- Backend enum values (status, scope, method) are not i18n strings — keep them as-is.
- Run `node scripts/check-i18n-coverage.mjs` to scan for potential hardcoded strings.
- Future UI copy additions must have an obvious home in `messages.ts` and a validation path.

## Flutter Parallel Client Track

The Vue 3 PWA remains the current production client. The Flutter client is a separate
application under `apps/flutter_kairo/`; it must not replace, weaken, or silently
change the PWA during its implementation.

For Flutter work, read these additional files before editing:

1. `apps/flutter_kairo/AGENTS.md`
2. `docs/flutter/PROJECT_STATUS.md`
3. `docs/flutter/FLUTTER_APP_ROADMAP.md`
4. `docs/flutter/FEATURE_PARITY.md`
5. `prompts/FLUTTER_CONTINUE_UNIVERSAL.md`

The Flutter client consumes the existing API contracts only. It never implements
authorization decisions locally, stores passwords, bypasses tenant boundaries, or
duplicates backend business rules. Android and Flutter Web are the first release
targets. iOS and desktop must remain architecture-ready, but are not release targets
until the roadmap explicitly promotes them.
