# Sprint Batch Autopilot

Status: Active — canonical execution policy for Kairo Roadmap V2, program S119–S128
(PWA-first, white-label SaaS).

This document defines how Kairo executes its canonical roadmap autonomously under
OpenCode. It is deliberately independent of any queue plugin: the repository batch
state is the single source of truth for sprint progress. Durable knowledge lives in
the repository (source, tests, migrations, contracts, ADRs, roadmap, automation state
and sprint handoffs), never in conversational memory.

## Components

| Component | Path |
| --- | --- |
| Active roadmap (human) | `docs/roadmap/KAIRO_V2_ROADMAP.md` |
| Active roadmap (machine) | `docs/roadmap/KAIRO_V2_ROADMAP.json` |
| Batch state machine | `scripts/sprint-batch/cli.mjs` |
| State and lock helpers | `scripts/sprint-batch/state.mjs` |
| Roadmap loader | `scripts/sprint-batch/roadmap.mjs` |
| Handoff schema and helpers | `scripts/sprint-batch/handoff.mjs` |
| Runner tests | `scripts/sprint-batch/sprint-batch.test.mjs` |
| Reports | `scripts/sprint-batch/report.mjs` |
| Environment doctor | `scripts/sprint-batch/doctor.mjs` |
| Single-sprint procedure | `prompts/KAIRO_SPRINT_EXECUTOR.md` |
| Batch loop procedure | `prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md` |
| OpenCode commands | `.opencode/commands/start-next-sprint.md`, `start-next-sprints.md`, `start-next-sprint-resume.md`, `sprint-batch-status.md`, `sprint-batch-resume.md`, `sprint-batch-stop.md` |

Runtime state is untracked:

```text
.kairo/sprint-batch/state.json      batch and sprint state
.kairo/sprint-batch/lock.json       single-runner lock with heartbeat
.kairo/sprint-batch/history.json    batch history
.kairo/sprint-batch/handoffs/       machine-readable handoff per completed sprint
.kairo/sprint-batch/reports/        per-sprint and per-batch reports
```

## Canonical operator commands

Natural language (interpreted by agents per `AGENTS.md`):

- **Start Next Sprint** → execute exactly one unfinished sprint.
- **Start Next Sprint N** → execute up to N consecutive sprints (`1 <= N <= 10`,
  capped at 10). If fewer remain, execute only those; never invent a sprint.
- **Start Next Sprint Resume** → resume the incomplete batch from its real state.
- **Start Next Sprints N** / **Start Next Sprints Resume** → backward-compatible
  aliases only.

OpenCode slash commands:

- `/start-next-sprint` (defaults to one sprint)
- `/start-next-sprint 5` (batch of up to five)
- `/start-next-sprint-resume`
- `/sprint-batch-status`
- `/sprint-batch-resume`
- `/sprint-batch-stop`

npm (run from the repository root):

```text
npm run sprint:batch:start -- 10
npm run sprint:batch:start -- --count 10
npm run sprint:batch:dry-run              # plan only, never mutates state
npm run sprint:batch:status
npm run sprint:batch:resume
npm run sprint:batch:stop
npm run sprint:batch:pause-human -- --reason "..."
npm run sprint:batch:reset -- --reason "..."   # archive an orphaned batch safely
npm run sprint:batch:repair -- --sprint <id> --reason "..."
npm run sprint:batch:handoff -- --sprint <id> --file <handoff.json>
npm run sprint:batch:preflight -- --sprint <id>
npm run sprint:batch:doctor
npm run sprint:batch:report
npm run sprint:batch:test
npm run sprint:next
```

Optional JSON output: `status --json`, `doctor --json`, `start --dry-run --json`.

## State machine

Runner statuses: `IDLE`, `RUNNING`, `PAUSED_FOR_HUMAN`, `BLOCKED`, `FAILED`,
`COMPLETED`.

Sprint statuses: `PENDING`, `PREFLIGHT`, `IMPLEMENTING`, `VERIFYING`,
`EVALUATING`, `COMPLETED`, `PAUSED`, `BLOCKED`, `FAILED`.

The state file records the batch id, roadmap, status, requested/completed/remaining
counts, current sprint and sprint status, runner status, last successful gate, pause
reason, last error, repair attempt, baseline SHA, lock owner, heartbeat, stop flag,
queue availability and a per-sprint array with status, attempts, repair attempts,
handoff path, timestamps, verification and summary.

## Context isolation and minimal loading

Each sprint runs as an independent execution unit with a fresh context. A batch must
not become one continuously expanding conversation: after PASS, the executor writes
the handoff, persists state, checkpoints, closes the sprint context and loads the next
sprint in a fresh context that only uses:

1. the active roadmap and the current sprint specification;
2. the immediately preceding handoff (plus earlier handoffs only when dependencies
   require them);
3. relevant architecture documentation and ADRs;
4. automation state;
5. only the source files, tests, contracts and migrations relevant to the sprint.

Never preload previous sprint transcripts, full logs, unrelated source trees or full
repository documentation. If a sprint risks exceeding a bounded context, split the
work into internal subtasks or specialized agents and keep only compact summaries in
the orchestrator.

## Sprint handoff (required for PASS)

At the end of every sprint, before `complete --verdict PASS`, persist a compact
machine-readable handoff:

```text
.kairo/sprint-batch/handoffs/sprint-<id>.json
```

Required fields:

```text
sprint_id
status
objective_completed
files_added
files_modified
files_removed
database_migrations
public_contract_changes
architecture_decisions
new_dependencies
configuration_changes
tests_added
tests_changed
tests_status
security_implications
known_limitations
remaining_followups
next_sprint_dependencies
commit_sha
timestamp
```

`complete --verdict PASS` refuses to run without a valid handoff for the active
sprint. Handoffs must never contain verbose reasoning, secrets or dumps. A different
agent must be able to resume the project from the roadmap, the latest handoff and the
repository alone.

## Concurrency and locking

- Only one batch runs at a time. `acquireLock` refuses to start a competing batch
  unless the existing lock is provably stale.
- The lock records batch id, PID, working directory, start time, heartbeat, phase and
  current sprint; takeover records `taken_over_at` and `taken_over_from`.
- A lock is stale when its heartbeat is older than 60 minutes, or older than 5
  minutes with a dead PID. `doctor` reports stale locks; `start` and `resume` take
  them over automatically. A crashed runner is recoverable without editing state
  files manually.
- Never delete a lock manually while an agent is known to be running.
- An orphaned batch (no active lock, no sprint in a running phase) can be closed
  safely with `reset`, which records it in history and lets the next
  `start --count N` create a fresh batch without hand-editing state files.
- `pause-human` sets `PAUSED_FOR_HUMAN` and releases the lock; `resume
  --human-resolved` is required to continue after the human action.

## Repair policy

- At most **3 repair attempts** for the same blocking failure, recorded through
  `cli.mjs repair`, which increments the sprint repair counter and re-enters
  `IMPLEMENTING`.
- After each failure, inspect the real cause, avoid repeating the previous change and
  validate with the smallest relevant check first; run full gates only once the local
  failure is fixed.
- After the third attempt the runner sets `PAUSED_FOR_HUMAN`, releases the lock and
  prints the human stop report. `resume --human-resolved` resets the counter only on
  an explicit operator decision.
- Never obtain a green sprint by deleting or skipping meaningful tests, weakening
  assertions, increasing tolerances arbitrarily, disabling security checks, swallowing
  exceptions, bypassing typing, removing validation or mocking the behavior the
  sprint exists to validate.

## Human stop report

When pausing for a human action, print and persist:

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

Pause immediately when a credential, secret, Firebase Console action, DNS change,
domain ownership verification, Play Console action, production access, irreversible
production operation, destructive migration, legal/commercial decision, material
architecture ambiguity, unavailable external dependency or explicitly required manual
device validation is needed.

## Idempotence and resume

All execution infrastructure is restart-safe. `Start Next Sprint Resume` reads the
persisted state, detects the paused checkpoint, inspects the actual repository state,
verifies completed work, creates a fresh context and resumes only unfinished work.
Re-running resume must not reapply completed migrations, recreate resources blindly,
duplicate generated configuration, duplicate notifications or repeat completed sprint
work. State is reconciled with the roadmap on resume so new roadmap sprints appear
without corrupting an existing batch.

## Atomic sprint checkpoint

A sprint is marked COMPLETED only after every Definition-of-Done gate passes:

```text
implementation
→ focused tests
→ required integration tests
→ lint/type/security checks
→ migrations validated
→ tenant isolation preserved
→ documentation updated
→ handoff written
→ state persisted
→ git checkpoint (when policy-safe)
→ next sprint in a fresh context
```

When a sprint reaches PASS and the batch still has remaining work, the orchestrator
closes the sprint context, persists the handoff and state, checkpoints, then starts
the next sprint in a fresh context. A BLOCKED or FAILED sprint never auto-transitions:
the batch stops and the state machine records the exact blocking reason.

## Fast failure and full gates

Use the smallest relevant validation first (changed-module tests, then integration,
then type/lint, then the full required gate). Full required gates MUST still run
before a PASS. The full-suite-oriented `gate_profile` values below are advisory
documentation, but can be used consistently in the roadmap:

- `docs`: documentation, status and roadmaps consistency.
- `backend`: ruff, mypy, pytest including tenant-isolation and permission tests.
- `web`: `npm run type-check`, `npm run build`, relevant Playwright specs.
- `pwa`: web gates plus Service Worker, offline, manifest and installability tests.
- `notifications`: backend plus Web Push, FCM, installation and deep-link tests.
- `whitelabel`: branding, manifest, host-resolution and tenant-isolation tests.
- `ci`: the default pipeline (Security, API, Contracts, Web, Production) locally or
  in CI, with deterministic dependency resolution.
- `release`: full-stack, real-infrastructure, real-device or explicitly
  human-validated gates.
- `full`: backend + web + security + i18n + contract checks; Flutter is optional
  reference only and never blocks the default pipeline.

Repository guards run in CI and locally:

```text
node scripts/check-sensitive-files.mjs
node scripts/check-i18n-parity.mjs
node scripts/check-i18n-coverage.mjs
node scripts/check-api-collection-paths.mjs
node scripts/check-capability-bundles.mjs
```

## Change minimization, migrations and dependencies

- Each sprint changes only what it needs. Unrelated refactors, formatting churn,
  dependency upgrades, renames and architectural rewrites are out of scope; record
  them as follow-ups in the handoff instead.
- Migrations need a deterministic file, an upgrade path, compatibility analysis, test
  coverage, recovery consideration and tenant-isolation verification. Never rewrite a
  migration already deployed.
- Do not add a dependency when existing tooling suffices; evaluate necessity,
  maintenance, security, bundle/runtime impact, licensing and platform support.
- Never commit secrets, service-account JSON, VAPID private keys, passwords, tokens
  or production credentials. Use existing configuration interfaces and `.env.example`
  placeholders.

## Git policy

- Never push, merge, force-push or rewrite remote history automatically.
- A local checkpoint commit may be created after a PASS when the tree was clean at
  sprint start. Blocked or failed sprints get no commit.
- Dangerous history remediation is prepared as instructions and marked
  `HUMAN_REQUIRED`; it is never executed automatically.

## Queue integration

Kairo supports OpenCode Queue when compatible with the installed runtime, but
correctness never depends on it. The batch state detects queue availability and
records it as `queue_available` in state and diagnostics. Commands such as
`/queue:list`, `/queue:stop` and `/queue:start` are operator conveniences only. The
native Kairo batch state machine remains the single source of truth.

## Diagnostics output

`npm run sprint:batch:doctor` reports Node, npm, Git, OpenCode and its version,
OpenCode config parseability, queue availability, roadmap parseability, roadmap path
validity, state and handoffs directory writability, competing batches, Python,
Flutter, Docker, critical project files and Firebase configuration status. Firebase is
reported as configured / not configured / unknown without ever printing secrets.
`npm run sprint:batch:test` runs the runner test suite.
