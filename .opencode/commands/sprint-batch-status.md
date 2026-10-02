---
description: Show the Kairo sprint batch state, current sprint and recent results
---

Show the current Kairo sprint batch status.

Do not rely on @file expansion. Read explicitly if needed.

Steps:

1. Run `npm run sprint:batch:status`.
2. Also run `node scripts/sprint-batch/cli.mjs next --json` when a batch is active,
   to report the next unfinished sprint and its dependencies.
3. Summarize concisely: batch id, roadmap, runner status, requested vs completed
   count, current sprint, sprint status/phase, repair attempt, last successful gate,
   stop-requested flag, pause reason, queue availability, remaining sprints in the
   batch, next unfinished sprint, and any blockers.

Do not modify any state in this command.
