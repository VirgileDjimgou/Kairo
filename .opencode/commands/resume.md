---
description: Fast session warm-up — one command instead of reading the whole documentation set
---

Start this session with the Kairo session brief instead of re-reading the repository
documentation.

1. Run `npm run session:brief`.
2. If it reports a next action that is executable (an unfinished sprint or a sprint
   to resume), state it in one sentence and continue with the user's request, reading
   only the files the task routing table names.
3. If it reports that all roadmap sprints are complete, say so immediately, name the
   operator-owned next actions, and ask the user what to work on. Do not investigate
   the roadmap, the batch state or the historical documents further.

Never read `IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`, `orgmind_prompt_pack/`,
`docs/flutter/**` or the handoff/report archives to "get oriented". Open one of them
only when the task itself needs it.

If `npm run session:brief` reports a stale or missing brief, regenerate it with
`npm run session:brief -- --write` and continue.
