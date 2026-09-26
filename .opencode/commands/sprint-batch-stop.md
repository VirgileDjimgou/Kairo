---
description: Request a safe-checkpoint stop of the running Kairo sprint batch
---

Stop the Kairo sprint batch at the nearest safe checkpoint.

Do not rely on @file expansion.

Steps:

1. Run `npm run sprint:batch:stop`.
2. Confirm the state with `npm run sprint:batch:status`.
3. Explain what happens next:
   - the running agent checks `stop_requested` before a new sprint, after
     implementation, and before starting the following sprint;
   - it does not interrupt an in-progress database write or abandon an intentionally
     partial refactor;
   - it reaches the nearest safe checkpoint, writes the sprint report, and sets the
     batch status to `paused`.
4. If no agent is actively running the batch, report that the batch is already paused.
