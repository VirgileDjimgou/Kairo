---
description: Execute N consecutive Kairo Roadmap V2 sprints (max 10) with hard gates
---

Start Next Sprints $ARGUMENTS.

Interpret `$ARGUMENTS` as the requested number of consecutive sprints `N`.

- If `$ARGUMENTS` is empty, treat `N` as 1.
- Accept `--count N` syntax as well as a bare number.
- If `N` is greater than 10, cap it at 10 and report the cap. Never silently execute
  more than 10 consecutive sprints in one autonomous batch.

You are the Kairo batch executor. Run a multi-sprint batch strictly sequentially,
one sprint at a time, with hard quality gates between sprints.

Do not rely on @file expansion. Read every required file explicitly with your file
tools before acting.

Required reading, in order:

1. `AGENTS.md`
2. `docs/roadmap/KAIRO_V2_ROADMAP.md` (sprint specifications and acceptance criteria)
3. `docs/roadmap/KAIRO_V2_ROADMAP.json` (machine-readable state of truth)
4. `docs/automation/SPRINT_BATCH_AUTOPILOT.md` (execution policy)
5. `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md` (batch loop algorithm)
6. `prompts/KAIRO_SPRINT_EXECUTOR.md` (single-sprint execution algorithm)
7. `PROJECT_STATUS.md` (product context only; the roadmap JSON wins for sprint state)

Then execute the batch:

1. Run `git status --short` and preserve unrelated uncommitted user changes.
2. Run `npm run sprint:batch:doctor`.
3. Initialize or resume the batch:
   `npm run sprint:batch:start -- --count N`
   (if an incomplete batch exists, use `npm run sprint:batch:resume` instead of
   starting a competing batch).
4. For each sprint in the batch, execute `prompts/KAIRO_SPRINT_EXECUTOR.md`, then
   record the result through `node scripts/sprint-batch/cli.mjs complete ...`.
5. Continue immediately to the next sprint when the current sprint passes. Do not
   wait for the operator to type "Start Next Sprint" again.
6. Stop automatically when the requested count is reached, when a stop condition is
   hit, or when `npm run sprint:batch:stop` has set `stop_requested`.
7. Print the KAIRO AUTONOMOUS BATCH REPORT at the end and state:
   "Autonomous batch limit reached. Manual operator evaluation is now required
   before the next batch." when the requested count completed successfully.
