# Kairo Agent Guide

This repository is designed to be continued from multiple agentic IDEs, including Codex, Cursor, and GitHub Copilot.

## Purpose

Use this file as the universal entry point before implementing or reviewing anything.

## Active Roadmap And Autopilot Aliases

Roadmap V2 (`docs/roadmap/KAIRO_V2_ROADMAP.md` and
`docs/roadmap/KAIRO_V2_ROADMAP.json`) is the canonical execution roadmap.
**Sprints 100–130 are complete.** The S119–S130 program (PWA-first, white-label
SaaS) is closed; no sprint is currently executable, so the next actions are
operator-owned: the manual pilot steps in `docs/pwa/COMBIS_PILOT_CHECKLIST.md`,
then a separate Roadmap V3 planning decision. `IMPLEMENTATION_ROADMAP.md` is the
historical Sprint 0–99 record. Execution policy lives in
`docs/automation/SPRINT_BATCH_AUTOPILOT.md`.

Do not restate this status from memory: `npm run session:brief` prints the
authoritative progress together with the batch state.

Interpret these operator phrases exactly:

- **Start Next Sprint** → execute exactly ONE unfinished Roadmap V2 sprint.
- **Start Next Sprint N** → execute up to `N` consecutive unfinished Roadmap V2
  sprints, one at a time, with hard quality gates between sprints. Default `N = 1`;
  allowed `1 <= N <= 10`; hard maximum 10 per autonomous batch. If `N > 10`, cap at
  10 and report the cap. If fewer remain, execute only those and never invent a
  sprint.
- **Start Next Sprint Resume** → resume the incomplete batch from its real state
  (never repeat a completed sprint, never restart a partially implemented sprint
  from scratch without inspecting it first).
- **Start Next Sprints N** and **Start Next Sprints Resume** are backward-compatible
  aliases of the two commands above.

Equivalent entry points: `/start-next-sprint [N]`, `/start-next-sprints N`,
`/start-next-sprint-resume`, `/sprint-batch-status`, `/sprint-batch-resume`,
`/sprint-batch-stop`, and the `npm run sprint:batch:*` commands.

Runtime batch state lives in `.kairo/sprint-batch/` and is untracked:

```text
.kairo/sprint-batch/state.json      batch and sprint state
.kairo/sprint-batch/lock.json       single-runner lock with heartbeat
.kairo/sprint-batch/history.json    batch history
.kairo/sprint-batch/handoffs/       one machine-readable handoff per completed sprint
.kairo/sprint-batch/reports/        per-sprint and per-batch reports
```

The machine roadmap is tracked. During a batch, record sprint transitions through
`scripts/sprint-batch/cli.mjs` (`preflight`, `verify`, `evaluate`, `handoff`,
`repair`, `complete`, `block`, `fail`, `pause-human`) so the state machine stays the
source of truth. A sprint cannot be marked PASS without its handoff file. Each
sprint runs in a fresh agent context and must be resumable by a different agent that
only reads the roadmap, the handoff and the repository.

## Session Warm-up (Read Order)

A new session has no memory of earlier sessions: this repository is the memory.
Reading the whole documentation set to get oriented costs more than a full context
window, so the warm-up is deliberately one page:

1. Run `npm run session:brief`. It prints the canonical program, the task routing
   table, the guard rails, live batch/sprint progress and the current git position.
   The same content is committed at `docs/ai/SESSION_BRIEF.md` (CI-guarded by
   `npm run session:brief:check`).
2. Read only the documents the task routing table names for the work at hand.
3. Inspect the code before making assumptions when behaviour is unclear.

Then read on demand, never "for orientation":

| If the task touches | Read |
| --- | --- |
| Tenant isolation, roles, authorization | `constitution/KAIRO_CONSTITUTION.md`, `services/api/app` |
| Architecture, module boundaries, ADRs | `docs/architecture/CURRENT_ARCHITECTURE.md`, `docs/architecture/decisions/` |
| API contract or endpoint change | `services/api/app`, `services/api/tests`, `npm run contracts:check` |
| Vue PWA screen or i18n copy | `apps/web/src/i18n/messages.ts`, Translation Governance below |
| Sprint execution policy | `docs/automation/SPRINT_BATCH_AUTOPILOT.md`, `prompts/KAIRO_SPRINT_EXECUTOR.md` |
| Product narrative or release history | the named section of `PROJECT_STATUS.md` (grep, do not read in full) |
| Historical rationale before Sprint 100 | the named section of `IMPLEMENTATION_ROADMAP.md` (grep only) |
| Resuming a specific sprint | that sprint's handoff in `.kairo/sprint-batch/handoffs/` |
| Frozen Flutter behaviour reference | `apps/flutter_kairo/AGENTS.md`, `docs/pwa/FLUTTER_TO_PWA_PARITY.md` |

Never read in full at session start: `IMPLEMENTATION_ROADMAP.md` (233 KB historical
record), `PROJECT_STATUS.md` (long product narrative), `orgmind_prompt_pack/`
(historical prompt pack superseded by `constitution/` and `docs/architecture/`),
`docs/flutter/**` (frozen legacy client, ADR-014), and the handoff/report archives.

When a task genuinely needs that historical corpus, delegate the reading to an
`explore` subagent and keep only its summary in the main context. Never pay for a
200 KB read to answer a question that needs two paragraphs.

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
2. Run `npm run session:brief` for orientation instead of reading the documentation
   set; open only the documents the task needs.
3. Confirm the active sprint from `docs/roadmap/KAIRO_V2_ROADMAP.json` and the batch
   state (`.kairo/sprint-batch/state.json`). Never infer progress from prose.
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

## Flutter Client — Frozen Legacy Reference

The Vue 3 PWA is the canonical client. The Flutter client under
`apps/flutter_kairo/` is **FROZEN as legacy/reference code**:

- it receives no new business features during S119–S128;
- it is not a blocking job of the default release pipeline;
- its source is preserved temporarily so it can be consulted for behavior,
  notification and parity reference;
- it must not replace, weaken, or silently change the PWA;
- any archival or deletion is a separate explicit decision after S128, never part of
  these sprints.

For reference-only inspection of Flutter work, read:

1. `apps/flutter_kairo/AGENTS.md`
2. `docs/flutter/PROJECT_STATUS.md`
3. `docs/flutter/FLUTTER_APP_ROADMAP.md`
4. `docs/flutter/FEATURE_PARITY.md`

The Flutter client consumes the existing API contracts only. It never implements
authorization decisions locally, stores passwords, bypasses tenant boundaries, or
duplicates backend business rules. The `Continue Next Sprint Implementation Flutter
App` command must not be used to start new Flutter business work while the freeze is
active.
