---
description: Execute exactly one next unfinished Kairo Roadmap V2 sprint
---

Start Next Sprint.

You are the Kairo sprint executor. This command runs exactly ONE unfinished sprint
from the active Roadmap V2, with the full quality gates.

Do not rely on @file expansion. Read every required file explicitly with your file
tools before acting.

Required reading, in order:

1. `AGENTS.md`
2. `docs/roadmap/KAIRO_V2_ROADMAP.md` (sprint specification and acceptance criteria)
3. `docs/roadmap/KAIRO_V2_ROADMAP.json` (machine-readable state of truth)
4. `docs/automation/SPRINT_BATCH_AUTOPILOT.md` (execution policy)
5. `prompts/KAIRO_SPRINT_EXECUTOR.md` (single-sprint execution algorithm)
6. `PROJECT_STATUS.md` (product context only; the roadmap JSON wins for sprint state)
7. `docs/ai/PROJECT_STATE.md` and `docs/ai/NEXT_SPRINT.md` if present

Then:

1. Run `git status --short` and preserve unrelated uncommitted user changes.
2. Run `npm run sprint:batch:doctor` and `npm run sprint:batch:status`.
3. Determine the next unfinished sprint with
   `node scripts/sprint-batch/cli.mjs next --json` (or read the roadmap directly if
   the batch engine reports no batch yet, then start a one-sprint batch with
   `npm run sprint:batch:start -- 1`).
4. Execute `prompts/KAIRO_SPRINT_EXECUTOR.md` for that single sprint.
5. Complete the sprint through the state machine:
   `node scripts/sprint-batch/cli.mjs complete --sprint <id> --verdict PASS --summary "<short summary>"`.
6. Stop after that one sprint. Do not continue into the following sprint in this
   command. Report the sprint verdict and the next unfinished sprint.
