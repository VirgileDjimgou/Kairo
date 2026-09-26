# Kairo Sprint Batch Executor

Use this procedure when the operator says **Start Next Sprints N** (or runs
`/start-next-sprints N`, or `npm run sprint:batch:start -- N`). It runs up to 10
consecutive Roadmap V2 sprints in one autonomous batch.

The per-sprint procedure is `prompts/KAIRO_SPRINT_EXECUTOR.md`. This file defines the
batch loop around it.

## Batch state machine

Runtime state lives outside the tracked product source:

```
.kairo/sprint-batch/state.json     batch and sprint state
.kairo/sprint-batch/lock.json      single-writer lock
.kairo/sprint-batch/history.json   batch id history
.kairo/sprint-batch/reports/       per-sprint and per-batch reports
```

Batch statuses: `idle`, `running`, `paused`, `blocked`, `completed`, `failed`.
Sprint statuses: `pending`, `implementing`, `verifying`, `evaluating`, `completed`,
`blocked`, `failed`.

Only one batch may run at a time. The lock records batch id, PID, working directory,
timestamp and a heartbeat. A stale lock may be taken over only after the heartbeat
and liveness checks in `scripts/sprint-batch/state.mjs` confirm no active owner.

## Batch loop

1. **Initialize or resume.** Run `npm run sprint:batch:doctor`, then
   `npm run sprint:batch:start -- --count N`. If an incomplete batch exists, resume
   it with `npm run sprint:batch:resume` rather than starting a competing batch.
2. **Determine the next unfinished sprint** from
   `docs/roadmap/KAIRO_V2_ROADMAP.json` plus batch state. Never skip a sprint whose
   dependency is incomplete.
3. **Execute the sprint** with `prompts/KAIRO_SPRINT_EXECUTOR.md`.
4. **Record the result** through the CLI (`complete`, `block`, or `fail`).
5. **Check `stop_requested`** before starting the next sprint and after
   implementation. If set, reach the nearest safe checkpoint, write the report and
   pause.
6. **Continue immediately** to the next sprint when the previous one passed and the
   requested count is not yet reached. Do not wait for the operator to type
   "Start Next Sprint" again.
7. **Stop automatically** when:
   - `completed_count` reaches `requested_count`;
   - a stop condition from `prompts/KAIRO_SPRINT_EXECUTOR.md` occurs;
   - a sprint is BLOCKED or FAILED (never jump over it);
   - `stop_requested` is set.
8. **Print the batch report** (`npm run sprint:batch:report`), including the
   KAIRO AUTONOMOUS BATCH REPORT structure, and the exact verdict.

When the requested count completes:

> Autonomous batch limit reached. Manual operator evaluation is now required before
> the next batch.

## Requested count rules

- Default `N = 1`.
- Allowed `1 <= N <= 10`.
- Hard maximum 10 consecutive sprints per autonomous batch.
- If `N > 10`, cap at 10 and report the cap; the operator can start another batch.

## Batch report structure

Persist and print:

```
KAIRO AUTONOMOUS BATCH REPORT

Batch ID:
Requested:
Completed:
Blocked:
First sprint:
Last sprint:
Duration:
Commits:
Migrations:
API changes:
UI changes:
Tests:
Builds:
Security:
Remaining known issues:
Next unfinished sprint:

Final batch verdict: PASS | BLOCKED | FAILED | PARTIAL
```

Per-sprint reports are written to `.kairo/sprint-batch/reports/` and contain the
sprint id, title, goal, files changed, architectural decisions, migrations, API/UI
changes, tests added/executed, builds, security checks, known limitations, acceptance
result, Git SHA and final verdict.

## Human approval boundaries

Autonomous work may edit source, add migrations, run local/test migrations, run
tests/builds, edit documentation, create fixtures, create local commits when safe,
refactor code and create scripts.

Autonomous work may NOT force-push, rewrite remote history, delete production data,
rotate production credentials, publish to the Play Store, promote Flutter Web into
production, change DNS, purchase services, expose new public endpoints bypassing
deployment controls or commit secrets. When such an action becomes necessary, prepare
everything up to the boundary, record `HUMAN_REQUIRED`, and continue only if later
roadmap work does not depend on the unapproved action.

## Reliability rule

Reliability beats sprint count. Ten verified sprints are useful; ten nominally
"completed" but untested sprints are not. Never sacrifice security, correctness,
tenant isolation, data integrity, tests or architectural coherence to reach the
requested count.
