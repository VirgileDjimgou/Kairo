# Kairo Sprint Executor

Use this procedure to execute exactly one sprint from
`docs/roadmap/KAIRO_V2_ROADMAP.json` in a fresh context. The batch executor
(`prompts/KAIRO_SPRINT_BATCH_EXECUTOR.md`) repeats it for consecutive sprints.

## Non-negotiable invariants

- Verified code and executable tests win over stale documentation.
- Preserve tenant isolation, backend-owned permissions, audit integrity and
  transaction correctness.
- Never weaken or delete a legitimate test, increase a golden tolerance, disable
  security validation, remove type checking or remove authorization checks to make a
  sprint pass.
- Never hardcode COMBIS as product logic; white-label identity comes from tenant
  configuration.
- Never rewrite remote Git history, force-push, delete production data or commit
  secrets.
- Preserve unrelated uncommitted user changes (`git status --short` first).
- Flutter is frozen as legacy/reference code: do not add business features there.

## Minimal context loading

Load only what this sprint needs:

1. `AGENTS.md` and `docs/automation/SPRINT_BATCH_AUTOPILOT.md`.
2. The sprint entry in `docs/roadmap/KAIRO_V2_ROADMAP.md` and the matching JSON entry.
3. The immediately preceding handoff in `.kairo/sprint-batch/handoffs/` (and earlier
   handoffs only when a dependency requires it).
4. The relevant architecture documentation and ADRs.
5. The source files, tests, contracts and migrations touched by this sprint.

Do not preload previous sprint transcripts, full logs, unrelated source trees or the
entire repository documentation. Use targeted search instead.

## Execution algorithm

### A. Preflight (fresh context)

1. Run `git status --short`; note user-owned changes that must be preserved.
2. Read the sprint entry and the previous handoff; verify the roadmap state.
3. Inspect the current repository state, relevant modules, tests and contracts.
4. Verify the previous sprint's claims against the actual code; the repository always
   wins over roadmap predictions.
5. Identify dependencies and create a small execution plan.

### B. Mark the sprint in progress

```
node scripts/sprint-batch/cli.mjs begin --sprint <id>
node scripts/sprint-batch/cli.mjs preflight --sprint <id>
```

If no batch exists yet, start one with the desired count first
(`npm run sprint:batch:start -- 1`). Dependencies must already be completed; no
sprint skipping is allowed.

### C. Implement only that sprint

- Make the smallest coherent change that satisfies the sprint.
- Keep the modular monolith shape: thin routers, service orchestration, repository
  isolation, provider abstractions, typed DTOs at boundaries.
- Preserve tenant isolation on every query and every new tenant-scoped resource
  (domains, branding, manifests, notifications, installations, Service Workers).
- Add regression coverage for the behavior you change while implementing.
- Run targeted tests continuously.

### D. Self-review

- Re-read the diff (`git diff`) as a reviewer.
- Check tenant scoping on every changed query.
- Check that no authorization decision moved into a frontend, manifest, Service
  Worker, notification payload or Firebase topic.
- Check multilingual coverage when user-facing strings changed.
- Check that no secret or operational data was introduced.

### E. Repair loop

If a gate fails because of this sprint's changes:

1. Record the attempt:
   `node scripts/sprint-batch/cli.mjs repair --sprint <id> --reason "<cause>"`.
2. Fix the root cause; never weaken the gate.
3. Re-run the smallest relevant check first, then the full required gate.
4. Maximum three repair attempts for the same meaningful failure. After the third,
   the runner pauses for a human automatically. Do not bypass this limit.

### F. Run the sprint gates

Run the gates required by the sprint's `gate_profile` (see
`docs/automation/SPRINT_BATCH_AUTOPILOT.md`). At minimum:

- Web/PWA changes: `npm run type-check`, `npm run build`, relevant Playwright specs,
  Service Worker/offline/manifest checks when touched.
- Backend changes: `ruff`, `mypy`, `pytest` for the touched area plus the backend
  suite when practical.
- Notification changes: tenant isolation, installation, deep-link and outbox tests.
- White-label changes: branding, manifest, host-resolution and tenant-isolation tests.
- Repository guards: `node scripts/check-sensitive-files.mjs`,
  `node scripts/check-i18n-coverage.mjs`, `node scripts/check-api-collection-paths.mjs`.
- i18n: FR/EN/DE key parity and no new hardcoded product strings.

### G. Update documentation

Update the documents affected by the sprint. Keep one obvious source of truth for
active roadmap status: `docs/roadmap/KAIRO_V2_ROADMAP.*` plus the batch state
machine.

### H. Write the handoff, then complete the sprint

```
node scripts/sprint-batch/cli.mjs handoff --sprint <id> --file <handoff.json>
node scripts/sprint-batch/cli.mjs verify --sprint <id>
node scripts/sprint-batch/cli.mjs evaluate --sprint <id>
node scripts/sprint-batch/cli.mjs complete --sprint <id> --verdict PASS --summary "<one-line summary>"
```

The handoff is mandatory for PASS and must contain every field listed in
`docs/automation/SPRINT_BATCH_AUTOPILOT.md`. A sprint is complete only when every
acceptance criterion is genuinely satisfied. The verdict is exactly one of `PASS`,
`BLOCKED`, `FAILED`. Never fabricate a PASS.

### I. Local checkpoint commit (optional, policy-safe)

A local commit MAY be created after a PASS when the working tree was clean at sprint
start and no unrelated user changes are mixed in. Format:

```
feat(kairo-s<id>): <short imperative summary>
refactor(kairo-s<id>): <short imperative summary>
```

Never push, never merge, never force-push, never commit for a blocked sprint.

## Stop conditions

Stop the batch and record BLOCKED/FAILED or pause for a human when:

- an unrecoverable build/test failure remains after three repair attempts;
- production credentials or a paid service are required;
- a destructive production migration or production data deletion is required;
- remote Git history rewriting is required;
- tenant isolation cannot be proven;
- a security regression is discovered;
- a requirement conflicts with the Kairo constitution;
- an architectural ambiguity could materially damage existing behavior;
- a user-owned dirty working tree conflicts with the sprint;
- the operator requested a stop;
- manual real-device validation is required and has no automated equivalent.

Do NOT stop merely because the work is large, many files need editing, tests take
time, documentation needs updating, or a refactoring is difficult.
