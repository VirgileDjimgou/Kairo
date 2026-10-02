---
description: Resume the incomplete Kairo sprint batch from its real state
---

Start Next Sprint Resume.

Resume the existing incomplete Kairo sprint batch. Do not restart a completed sprint
and do not restart a partially implemented sprint from scratch without inspecting it
first.

Do not rely on @file expansion. Read every required file explicitly.

Required reading, in order:

1. `AGENTS.md`
2. `docs/automation/SPRINT_BATCH_AUTOPILOT.md`
3. `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md`
4. `prompts/KAIRO_SPRINT_EXECUTOR.md`
5. `docs/roadmap/KAIRO_V2_ROADMAP.json` and `docs/roadmap/KAIRO_V2_ROADMAP.md`
6. the latest sprint handoff in `.kairo/sprint-batch/handoffs/`

Then:

1. Run `git status --short` and preserve unrelated uncommitted user changes.
2. Run `npm run sprint:batch:status` and `npm run sprint:batch:doctor`.
3. Inspect the incomplete batch: batch state, `git diff`, the latest sprint handoff
   and report under `.kairo/sprint-batch/`, and the relevant tests.
4. If the current sprint is only partially implemented, continue it from its real
   state instead of starting from scratch.
5. If the batch is `paused_for_human`, resolve the blocking condition first; only then
   run `npm run sprint:batch:resume -- --human-resolved`.
6. Continue the batch loop per `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md` until the
   requested count is reached, a stop condition occurs, a human-only action is
   required, or `stop_requested` is set.
