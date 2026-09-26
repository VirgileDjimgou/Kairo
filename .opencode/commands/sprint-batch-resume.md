---
description: Resume the incomplete Kairo sprint batch from a safe checkpoint
---

Start Next Sprints Resume.

Resume the existing incomplete Kairo sprint batch. Do not restart a completed sprint.

Do not rely on @file expansion. Read every required file explicitly.

Required reading, in order:

1. `AGENTS.md`
2. `docs/automation/SPRINT_BATCH_AUTOPILOT.md`
3. `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md`
4. `prompts/KAIRO_SPRINT_EXECUTOR.md`
5. `docs/roadmap/KAIRO_V2_ROADMAP.json`
6. `docs/roadmap/KAIRO_V2_ROADMAP.md`

Then:

1. Run `git status --short` and preserve unrelated uncommitted user changes.
2. Run `npm run sprint:batch:status` and `npm run sprint:batch:doctor`.
3. Inspect the incomplete batch: batch state, `git diff`, the latest sprint report
   under `.kairo/sprint-batch/reports/`, and the relevant tests.
4. If the current sprint is only partially implemented, continue it from its real
   state instead of starting from scratch.
5. Run `npm run sprint:batch:resume`.
6. Continue the batch loop per `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md` until the
   requested count is reached, a stop condition occurs, or `stop_requested` is set.
