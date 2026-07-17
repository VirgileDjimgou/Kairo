# Audit Weaknesses — 2026-07-17

This note records the main weaknesses confirmed during the July 17, 2026 audit
pass used to define the next dense delivery cycle.

## Scope

- Audit basis: repository code, continuity docs, build scripts, CI config, and
  prompt/continuation assets
- Verification level: targeted repository inspection, not a full fresh-stack
  production audit

## Confirmed Weaknesses

### 1. Continuity documentation drift

Status: Confirmed

Evidence:

- `README.md` still exposed `## Delivery Status (Validated 2026-07-16)` with
  `Sprint 77` as current while `PROJECT_STATUS.md` already marks Sprint 85 as
  completed on July 17, 2026
- `docs/ai/PROMPT_UNIVERSAL_NEXT_SPRINT.md` still referenced the old
  Sprint-54 continuity state before this audit pass

Impact:

- High risk of wrong sprint selection by future agents or maintainers
- Reduces trust in the repo as a source of execution truth

### 2. Prompt and handoff sprawl

Status: Confirmed

Evidence:

- `prompts/` contains multiple overlapping entry prompts:
  `CONTINUER_KAIRO_PROMPT_FR.md`, `KAIRO_CONTINUE_5_SPRINTS.md`,
  `KAIRO_CONTINUE_UNIVERSAL.md`, `Master_Prompt_Codex.md`
- `docs/ai/` also contained a prompt file with stale state

Impact:

- Too many similar prompts increase operator ambiguity
- Future sessions may use an incomplete or obsolete continuation path

### 3. Validation baselines are intentionally partial

Status: Confirmed

Evidence:

- `services/api/pyproject.toml` keeps `ignore_missing_imports = true`
- `.github/workflows/ci.yml` runs Ruff and Mypy only on a selected backend
  subset instead of the broader API surface
- `apps/web/package.json` exposes browser checks mainly through the localized
  Playwright pack, while critical multi-role business journeys remain outside
  the automated baseline

Impact:

- Good non-regression coverage exists, but quality gates are not yet broad
  enough for stronger production confidence

### 4. Backend role model is ahead of frontend role experience

Status: Confirmed

Evidence:

- `PROJECT_STATUS.md` explicitly lists frontend role-navigation parity as a
  remaining risk
- The repository already contains canonical capabilities and multiple role
  workspaces, but the project still documents gaps in fine-grained frontend
  reflection of those permissions

Impact:

- Security remains backend-enforced, which is good
- User experience and discoverability still lag behind the permission model

### 5. Notification delivery became real faster than operator triage matured

Status: Confirmed

Evidence:

- Sprint 79 through Sprint 85 progressively added live channels, delivery
  evidence, callback reconciliation, replay safety, and controlled polling
- `PROJECT_STATUS.md` still identifies stale pending and failed delivery triage
  as a remaining gap

Impact:

- Delivery trust improved
- Day-to-day operator follow-up remains too manual for a polished mature
  association product

### 6. Production confidence is stronger than deployment automation evidence

Status: Confirmed

Evidence:

- `docker-compose.yml`, production env examples, smoke scripts, and healthchecks
  are present
- `.github/workflows/ci.yml` does not yet validate the production Docker build
  and smoke path end to end

Impact:

- Self-hosted discipline is good
- Release confidence still depends too much on manual validation

## Strong Probabilities

### 7. Privacy and compliance workflows are still more implicit than productized

Status: Strongly probable

Evidence:

- The project contains multi-tenant isolation, audit, export, and role-aware
  access boundaries
- There is no dedicated visible continuity artifact yet for retention,
  deletion/export governance, or privacy operations as a coherent product track

Impact:

- Technical safety is already good
- Operational readiness for real association boards may still require a more
  explicit governance layer

## Non-Issues Worth Preserving

- Backend authorization remains the primary enforcement point
- Tenant isolation is consistently treated as non-negotiable
- Provider abstractions are already strong enough to extend safely
- SQLite-first backend testing is a real asset and should be preserved
- The modular monolith remains the right complexity level for this product stage
