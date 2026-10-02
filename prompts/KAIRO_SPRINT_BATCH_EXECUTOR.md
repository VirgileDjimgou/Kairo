# Kairo Sprint Batch Executor

Use this procedure when the operator says **Start Next Sprint N** (or
**Start Next Sprints N**, `/start-next-sprint N`, or
`npm run sprint:batch:start -- N`). It runs up to 10 consecutive Roadmap V2 sprints
in one autonomous batch. **Start Next Sprint** alone means exactly one sprint.

The per-sprint procedure is `prompts/KAIRO_SPRINT_EXECUTOR.md`. This file defines the
batch loop around it.

## Batch state machine

Runtime state lives outside the tracked product source:

```text
.kairo/sprint-batch/state.json      batch and sprint state
.kairo/sprint-batch/lock.json       single-writer lock
.kairo/sprint-batch/history.json    batch id history
.kairo/sprint-batch/handoffs/       machine-readable handoff per completed sprint
.kairo/sprint-batch/reports/        per-sprint and per-batch reports
```

Runner statuses: `IDLE`, `RUNNING`, `PAUSED_FOR_HUMAN`, `BLOCKED`, `FAILED`,
`COMPLETED`.
Sprint statuses: `PENDING`, `PREFLIGHT`, `IMPLEMENTING`, `VERIFYING`, `EVALUATING`,
`COMPLETED`, `PAUSED`, `BLOCKED`, `FAILED`.

Only one batch may run at a time. The lock records batch id, PID, working directory,
timestamp, heartbeat and current sprint. A stale lock may be taken over only after the
heartbeat and liveness checks in `scripts/sprint-batch/state.mjs` confirm no active
owner. A crashed runner is recoverable through `resume`, never by hand-editing state.

## Context isolation (mandatory)

Every sprint runs as an independent execution unit with a fresh context:

```text
Batch Orchestrator
├── fresh context → sprint N → verify → handoff → checkpoint
├── fresh context → sprint N+1 → verify → handoff → checkpoint
└── ...
```

After PASS: write the handoff, persist state, checkpoint, close the sprint context,
then load the next sprint with only the minimal required files. Never carry full
sprint reasoning into the next iteration. A different agent with no access to this
conversation must be able to resume from the roadmap, the handoff and the repository.

## Batch loop

1. **Initialize or resume.** Run `npm run sprint:batch:doctor`, then
   `npm run sprint:batch:start -- --count N`. If an incomplete batch exists, resume
   it with `npm run sprint:batch:resume` (or `--human-resolved` only when the operator
   explicitly states the blocking human action is complete) rather than starting a
   competing batch. `npm run sprint:batch:dry-run` previews the next sprint without
   mutating state.
2. **Determine the next unfinished sprint** from
   `docs/roadmap/KAIRO_V2_ROADMAP.json` plus batch state. Never skip a sprint whose
   dependency is incomplete.
3. **Execute the sprint** with `prompts/KAIRO_SPRINT_EXECUTOR.md`.
4. **Verify and repair.** On a gate failure, record the attempt with
   `node scripts/sprint-batch/cli.mjs repair --sprint <id> --reason "<cause>"` and fix
   the root cause. Maximum three repair attempts for the same meaningful failure.
5. **Write the handoff** before requesting PASS:
   `node scripts/sprint-batch/cli.mjs handoff --sprint <id> --file <handoff.json>`.
6. **Record the result** through the CLI (`complete`, `block`, or `fail`).
7. **Check `stop_requested`** before starting the next sprint and after
   implementation. If set, reach the nearest safe checkpoint, write the report and
   pause.
8. **Continue immediately** to the next sprint when the previous one passed and the
   requested count is not yet reached. Do not wait for the operator to type
   "Start Next Sprint" again.
9. **Stop automatically** when:
   - `completed_count` reaches `requested_count`;
   - a stop condition from `prompts/KAIRO_SPRINT_EXECUTOR.md` occurs;
   - a sprint is BLOCKED or FAILED (never jump over it);
   - `stop_requested` is set;
   - the repair limit is reached (`PAUSED_FOR_HUMAN`);
   - a human-only action is required.
10. **Print the batch report** (`npm run sprint:batch:report`), including the
    KAIRO AUTONOMOUS BATCH REPORT structure, and the exact verdict.

When the requested count completes:

> Autonomous batch limit reached. Manual operator evaluation is now required before
> the next batch.

## Requested count rules

- Default `N = 1`.
- Allowed `1 <= N <= 10`.
- Hard maximum 10 consecutive sprints per autonomous batch.
- If `N > 10`, cap at 10 and report the cap; the operator can start another batch.
- If fewer than N unfinished sprints remain, execute only those. Never invent a
  sprint.

## Human stop report

When pausing for a human action, persist and print:

```text
Completed:
Current sprint:
Current checkpoint:
Remaining requested batch:
Blocking reason:
Exact human action required:
How to validate completion:
Resume command: Start Next Sprint Resume
```

Pause immediately for credentials, secrets, Firebase Console actions, DNS changes,
domain verification, Play Console actions, production access, irreversible production
operations, destructive migrations, legal/commercial decisions, material architecture
ambiguity, unavailable external dependencies or explicitly required manual device
validation. Include the completed work and the current checkpoint so the operator
never has to reconstruct project state.

Do NOT pause merely because the work is large, many files need editing, tests take
time, documentation needs updating, or a refactoring is difficult.

## Batch report structure

Persist and print:

```text
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

Per-sprint reports are written to `.kairo/sprint-batch/reports/`; the machine-readable
handoff is written to `.kairo/sprint-batch/handoffs/sprint-<id>.json` and is required
before a PASS.

## Human approval boundaries

Autonomous work may edit source, add migrations, run local/test migrations, run
tests/builds, edit documentation, create fixtures, create local commits when safe,
refactor code and create scripts.

Autonomous work may NOT force-push, rewrite remote history, delete production data,
rotate production credentials, publish to the Play Store, promote Flutter Web into
production, change DNS, purchase services, expose new public endpoints bypassing
deployment controls or commit secrets. When such an action becomes necessary, prepare
everything up to the boundary, call
`node scripts/sprint-batch/cli.mjs pause-human --reason "<exact action>"`, and
continue only if later roadmap work does not depend on the unapproved action.

## Reliability rule

Reliability beats sprint count. Ten verified sprints are useful; ten nominally
"completed" but untested sprints are not. Never sacrifice security, correctness,
tenant isolation, data integrity, tests or architectural coherence to reach the
requested count. Never fabricate a PASS.
