# Kairo Sprint Executor

Use this procedure to execute exactly one sprint from
`docs/roadmap/KAIRO_V2_ROADMAP.json`. The batch executor
(`prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md`) repeats it for consecutive sprints.

## Non-negotiable invariants

- Verified code and executable tests win over stale documentation.
- Preserve tenant isolation, backend-owned permissions, audit integrity and
  transaction correctness.
- Never weaken or delete a legitimate test, increase a golden tolerance, disable
  security validation, remove type checking or remove authorization checks to make a
  sprint pass.
- Never hardcode COMBIS as product logic.
- Never rewrite remote Git history, force-push, delete production data or commit
  secrets.
- Preserve unrelated uncommitted user changes (`git status --short` first).

## Execution algorithm

### A. Load context

1. Run `git status --short`; note user-owned changes that must be preserved.
2. Read `AGENTS.md`, the sprint entry in `docs/roadmap/KAIRO_V2_ROADMAP.md`, the
   matching JSON entry, and `docs/automation/SPRINT_BATCH_AUTOPILOT.md`.
3. Read the relevant application code and tests before editing anything.
4. Inspect `PROJECT_STATUS.md` and `docs/ai/PROJECT_STATE.md` for product context.
   For sprint state, the roadmap JSON and the batch state machine are the source of
   truth.

### B. Mark the sprint implementing

```
node scripts/sprint-batch/cli.mjs begin --sprint <id>
```

If no batch exists yet, start one with the desired count first
(`npm run sprint:batch:start -- 1`). Dependencies must already be completed; no
sprint skipping is allowed.

### C. Implement only that sprint

- Inspect first, then make the smallest coherent change that satisfies the sprint.
- Keep the modular monolith shape: thin routers, service orchestration, repository
  isolation, provider abstractions, typed DTOs at boundaries.
- Add regression coverage for the behavior you change while implementing.
- Run targeted tests continuously.

### D. Self-review

- Re-read the diff (`git diff`) as a reviewer.
- Check tenant scoping on every changed query.
- Check that no authorization decision moved into a frontend.
- Check multilingual coverage when user-facing strings changed.
- Check that no secret or operational data was introduced.

### E. Repair loop

If a gate fails because of this sprint's changes:

1. Fix the root cause; do not weaken the gate.
2. Re-run the failing checks.
3. Maximum three repair rounds for the same meaningful failure.
4. If the same failure survives three rounds, mark the sprint BLOCKED and stop.

### F. Run the sprint gates

Run the gates required by the sprint's `gate_profile`. At minimum:

- Backend changes: `ruff`, `mypy`, `pytest` for the touched area plus the backend
  suite when practical.
- Web changes: `npm run type-check`, `npm run build` and the relevant Playwright
  specs in `apps/web`.
- Flutter changes: `flutter analyze`, `flutter test`, and the relevant Android/Web
  build when touched.
- Repository guards: `node scripts/check-sensitive-files.mjs`,
  `node scripts/check-i18n-coverage.mjs`, `node scripts/check-api-collection-paths.mjs`.
- Security: tenant isolation tests and permission tests for the touched area.
- i18n: FR/EN/DE key parity and no new hardcoded product strings.

### G. Update documentation

Update the documents affected by the sprint. Keep one obvious source of truth for
active roadmap status: `docs/roadmap/KAIRO_V2_ROADMAP.*` plus the batch state
machine. `PROJECT_STATUS.md` and `docs/ai/NEXT_SPRINT.md` must never pretend an old
sprint is current after the V2 migration.

### H. Complete the sprint

```
node scripts/sprint-batch/cli.mjs verify --sprint <id>
node scripts/sprint-batch/cli.mjs evaluate --sprint <id>
node scripts/sprint-batch/cli.mjs complete --sprint <id> --verdict PASS --summary "<one-line summary>"
```

A sprint is complete only when every acceptance criterion is genuinely satisfied.
The verdict is exactly one of `PASS`, `BLOCKED`, `FAILED`.

### I. Local checkpoint commit (optional, policy-safe)

A local commit MAY be created after a PASS when the working tree was clean at sprint
start and no unrelated user changes are mixed in. Format:

```
feat(kairo-s<id>): <short imperative summary>
refactor(kairo-s<id>): <short imperative summary>
```

Never push, never merge, never force-push, never commit for a blocked sprint.

## Stop conditions

Stop the batch and record BLOCKED/FAILED when:

- an unrecoverable build/test failure remains after repair attempts;
- production credentials or a paid service are required;
- a destructive production migration or production data deletion is required;
- remote Git history rewriting is required;
- tenant isolation cannot be proven;
- a security regression is discovered;
- a requirement conflicts with the Kairo constitution;
- an architectural ambiguity could materially damage existing behavior;
- a user-owned dirty working tree conflicts with the sprint;
- the operator requested a stop.

Do NOT stop merely because the work is large, many files need editing, tests take
time, documentation needs updating, or a refactoring is difficult.
