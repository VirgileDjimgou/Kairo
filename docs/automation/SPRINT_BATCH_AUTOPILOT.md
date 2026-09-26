# Sprint Batch Autopilot

Status: Active — canonical execution policy for Kairo Roadmap V2.

This document defines how Kairo executes Roadmap V2 autonomously under OpenCode. It
is deliberately independent of any queue plugin: the repository batch state is the
single source of truth for sprint progress.

## Components

| Component | Path |
| --- | --- |
| Active roadmap (human) | `docs/roadmap/KAIRO_V2_ROADMAP.md` |
| Active roadmap (machine) | `docs/roadmap/KAIRO_V2_ROADMAP.json` |
| Batch state machine | `scripts/sprint-batch/cli.mjs` |
| State and lock helpers | `scripts/sprint-batch/state.mjs` |
| Roadmap loader | `scripts/sprint-batch/roadmap.mjs` |
| Reports | `scripts/sprint-batch/report.mjs` |
| Environment doctor | `scripts/sprint-batch/doctor.mjs` |
| Single-sprint procedure | `prompts/KAIRO_SPRINT_EXECUTOR.md` |
| Batch loop procedure | `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md` |
| OpenCode commands | `.opencode/commands/start-next-sprint.md`, `start-next-sprints.md`, `sprint-batch-status.md`, `sprint-batch-resume.md`, `sprint-batch-stop.md` |

Runtime state is untracked:

```
.kairo/sprint-batch/state.json
.kairo/sprint-batch/lock.json
.kairo/sprint-batch/history.json
.kairo/sprint-batch/reports/
```

## Operator commands

Natural language (interpreted by agents per `AGENTS.md`):

- **Start Next Sprint** → execute exactly one next unfinished sprint.
- **Start Next Sprints N** → execute N consecutive sprints (`1 <= N <= 10`, capped).
- **Start Next Sprints Resume** → resume the incomplete batch from a safe checkpoint.

OpenCode slash commands:

- `/start-next-sprint`
- `/start-next-sprints 10`
- `/sprint-batch-status`
- `/sprint-batch-resume`
- `/sprint-batch-stop`

npm (run from the repository root):

```text
npm run sprint:batch:start -- 10
npm run sprint:batch:start -- --count 10
npm run sprint:batch:status
npm run sprint:batch:resume
npm run sprint:batch:stop
npm run sprint:batch:doctor
npm run sprint:batch:report
npm run sprint:next
```

Optional JSON output: `node scripts/sprint-batch/cli.mjs status --json` and
`node scripts/sprint-batch/cli.mjs doctor --json`.

## State machine

Batch statuses: `idle`, `running`, `paused`, `blocked`, `completed`, `failed`.
Sprint statuses: `pending`, `implementing`, `verifying`, `evaluating`, `completed`,
`blocked`, `failed`.

The state file records `batch_id`, `roadmap`, `status`, `requested_count`,
`completed_count`, `current_sprint`, `started_at`, `updated_at`, `baseline_sha`,
`stop_requested`, `queue_available` and a per-sprint array with `status`, `attempts`,
timestamps, `verification`, and `summary`.

## Concurrency

- Only one batch runs at a time. `acquireLock` refuses to start a competing batch
  unless the existing lock is provably stale.
- The lock records batch id, PID, working directory, start time, heartbeat and
  current phase. Every CLI phase transition refreshes the heartbeat.
- A lock is stale when its heartbeat is older than 60 minutes, or older than 5
  minutes with a dead PID. `doctor` reports a stale lock as a warning; `start` and
  `resume` take it over.
- Never delete a lock manually while an agent is known to be running.

## Execution guarantees

- No sprint skipping: dependencies declared in the roadmap JSON must be completed.
- A blocked sprint blocks the batch. The loop never jumps to the following sprint.
- Repair policy: at most three repair rounds per meaningful failure. Tests are never
  deleted, skipped, loosened or disabled to obtain green output.
- Immediately after a PASS the executor continues with the next sprint in the batch,
  without waiting for operator input.
- `npm run sprint:batch:stop` sets `stop_requested`; the agent checks it before a
  new sprint, after implementation and before starting the next sprint, then pauses
  at the nearest safe checkpoint.

## Quality gates

Gate profiles referenced by the roadmap JSON:

- `baseline` (S100): ruff, mypy, pytest, web type-check/build, web localization +
  role Playwright packs, Flutter analyze/test/build, sensitive-file scanner.
- `backend`: ruff, mypy, pytest including tenant-isolation and permission tests.
- `web`: `npm run type-check`, `npm run build`, relevant Playwright specs.
- `full`: backend + web + Flutter + security + i18n + contract checks.
- `release` (S118): full regression, accessibility, restore drill, rollback runbook.

Repository guards run in CI and locally:

```text
node scripts/check-sensitive-files.mjs
node scripts/check-i18n-parity.mjs
node scripts/check-i18n-coverage.mjs
node scripts/check-api-collection-paths.mjs
node scripts/check-capability-bundles.mjs
```

## Queue integration

Kairo supports OpenCode Queue when it is compatible with the installed runtime, but
correctness never depends on it. The batch state detects queue availability and
records it as `queue_available` in state and diagnostics. Commands such as
`/queue:list`, `/queue:stop` and `/queue:start` remain operator conveniences only.

Compatibility record (OpenCode 1.18.32, 2026-09-25): `opencode-queue@0.15.1` is a
TypeScript plugin installed through the runtime and requires an OpenCode restart.
Installing or enabling it mid-session could destabilise the operator's running
session, so it is deliberately not enabled automatically. `QUEUE_AVAILABLE=false`.
The native Kairo batch state machine remains the single source of truth.

Optional operator enablement (requires an OpenCode restart, never required for
correctness):

```jsonc
{
  "plugin": ["opencode-queue"]
}
```

Add that entry to `opencode.json`, restart OpenCode, and verify with
`npm run sprint:batch:doctor`. The batch engine will then report
`queue_available: true`.

## Git policy

- Never push, merge, force-push or rewrite remote history automatically.
- A local checkpoint commit may be created after a PASS when the tree was clean at
  sprint start. Blocked sprints get no commit.
- Dangerous history remediation (for example `git filter-repo`) is prepared as
  instructions and marked `HUMAN_REQUIRED`; it is never executed automatically.

## Human approval boundaries

Autonomous work may: edit source, add migrations, run local/test migrations, run
tests and builds, edit documentation, create fixtures, refactor code, and create
local commits when safe.

Autonomous work may not: force-push, rewrite remote history, delete production data,
rotate production credentials, publish to the Play Store, promote Flutter Web into
production, change DNS, purchase services, expose endpoints outside the existing
deployment controls, or commit secrets.

When such an action becomes necessary, prepare everything up to the boundary, record
`HUMAN_REQUIRED`, and continue only if later roadmap work does not depend on it.

## Diagnostics output

`npm run sprint:batch:doctor` reports Node, npm, Git, OpenCode and its version,
OpenCode config parseability, queue availability, roadmap parseability, state-dir
writability, competing batches, Python, Flutter, Docker, critical project files and
Firebase configuration status. Firebase is reported as configured / not configured /
unknown without ever printing secrets.
