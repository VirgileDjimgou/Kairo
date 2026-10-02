---
description: Execute N next unfinished Kairo roadmap sprints (default 1, max 10)
---

Start Next Sprint $ARGUMENTS.

Interpret `$ARGUMENTS` as the requested number of consecutive sprints `N`.

- If `$ARGUMENTS` is empty, treat `N` as 1.
- Accept `--count N` syntax as well as a bare number.
- If `N` is greater than 10, cap it at 10 and report the cap. Never silently execute
  more than 10 consecutive sprints in one autonomous batch.
- If fewer than `N` unfinished sprints remain, execute only those and never invent a
  sprint.

You are the Kairo sprint batch executor. The active program is S119–S128
(PWA-first, white-label SaaS). The Vue 3 PWA is the canonical client; Flutter is
frozen as legacy/reference code and must not block the default release pipeline.

Do not rely on @file expansion. Read every required file explicitly with your file
tools before acting.

Required reading, in order:

1. `AGENTS.md`
2. `docs/roadmap/KAIRO_V2_ROADMAP.md` (sprint specifications and acceptance criteria)
3. `docs/roadmap/KAIRO_V2_ROADMAP.json` (machine-readable state of truth)
4. `docs/automation/SPRINT_BATCH_AUTOPILOT.md` (execution policy)
5. `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md` (batch loop algorithm)
6. `prompts/KAIRO_SPRINT_EXECUTOR.md` (single-sprint execution algorithm)
7. the previous sprint handoff in `.kairo/sprint-batch/handoffs/` when one exists

Then execute the batch:

1. Run `git status --short` and preserve unrelated uncommitted user changes.
2. Run `npm run sprint:batch:doctor`.
3. Preview with `npm run sprint:batch:dry-run` when useful, then initialize or resume
   the batch: `npm run sprint:batch:start -- --count N` (if an incomplete batch
   exists, use `npm run sprint:batch:resume` instead of starting a competing batch).
4. For each sprint, execute `prompts/KAIRO_SPRINT_EXECUTOR.md` in a fresh context:
   preflight, implement, repair (max 3 attempts), write the handoff, then record the
   result through `node scripts/sprint-batch/cli.mjs complete ...`. A PASS without a
   handoff is refused by the runner.
5. Continue immediately to the next sprint when the current one passes. Do not wait
   for the operator to type "Start Next Sprint" again.
6. Stop automatically when the requested count is reached, when a stop condition is
   hit, when `npm run sprint:batch:stop` set `stop_requested`, when a human-only
   action is required (`pause-human`), or when the repair limit is reached.
7. Print the KAIRO AUTONOMOUS BATCH REPORT at the end and state:
   "Autonomous batch limit reached. Manual operator evaluation is now required
   before the next batch." when the requested count completed successfully.
