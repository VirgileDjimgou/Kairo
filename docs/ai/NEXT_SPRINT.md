# Next Sprint

**Do not track sprint status in this file.** Sprint status has exactly one source
of truth: `docs/roadmap/KAIRO_V2_ROADMAP.json` plus the batch state machine.

## How to determine the next sprint

```bash
npm run sprint:next        # resolve and print the next unfinished sprint
npm run sprint:batch:status
```

or read the roadmap directly: the first sprint in `docs/roadmap/KAIRO_V2_ROADMAP.json`
whose entry is not recorded as `completed` in `.kairo/sprint-batch/state.json`
(when a batch is active).

## Rules

- The active program is S119–S128 (PWA-first, white-label SaaS); the Vue 3 PWA is the
  canonical client and Flutter is frozen as legacy/reference code.
- Execute exactly one sprint at a time unless the operator requests a batch
  (`Start Next Sprint N`, `1 <= N <= 10`; `Start Next Sprints N` is a
  backward-compatible alias).
- Dependencies in the roadmap JSON must be completed first; never skip a sprint.
- A blocked sprint blocks the batch; record it through
  `scripts/sprint-batch/cli.mjs` and stop.
- A PASS requires a machine-readable handoff in `.kairo/sprint-batch/handoffs/`.

## Historical note

The Sprint 0–99 record lives in `IMPLEMENTATION_ROADMAP.md` (read-only) and the
historical sections of `PROJECT_STATUS.md`. Earlier content of this file
described Sprint 98 and was retired because it contradicted the real state.
