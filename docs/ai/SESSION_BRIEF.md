<!-- GENERATED FILE - do not edit by hand. -->
<!-- Regenerate: npm run session:brief -- --write -->
<!-- Drift guard: npm run session:brief:check (CI) -->

# Kairo Session Brief

Orientation only. Sprint progress, batch state and git position are printed by
`npm run session:brief`; they are untracked runtime state and are never stored here.

## Start here

1. Run `npm run session:brief` (one command: this page plus live state).
2. Read only the documents named by the task routing table below.
3. Never read the whole documentation set to "get oriented".

## Canonical program

| Field | Value |
| --- | --- |
| Roadmap | `KAIRO_V2` version 3 |
| Active program | `PWA_FIRST_WHITE_LABEL_SAAS` |
| Program range | S119-S130 |
| Declared sprints | 31 (S100-S130) |
| Sprint file | `docs/roadmap/KAIRO_V2_ROADMAP.json` |
| Historical record | `IMPLEMENTATION_ROADMAP.md` (read-only) |

Objective: CONSOLIDATE the Vue 3 PWA as the canonical client, freeze Flutter as legacy reference, and make Kairo a production-oriented multi-tenant white-label SaaS without replacing the modular monolith, weakening tenant isolation, or rewriting remote history.

Sprint completion has exactly two sources of truth: the roadmap JSON plus
`.kairo/sprint-batch/state.json` (untracked) and the handoff in
`.kairo/sprint-batch/handoffs/`. Never infer completion from prose, file dates or
`PROJECT_STATUS.md` narratives.

## Task routing

| If the task touches | Read only this |
| --- | --- |
| Tenant isolation, roles, authorization | constitution/KAIRO_CONSTITUTION.md, services/api/app |
| Architecture, module boundaries, ADRs | docs/architecture/CURRENT_ARCHITECTURE.md, docs/architecture/decisions/ |
| API contract or endpoint change | services/api/app, services/api/tests, npm run contracts:check |
| Vue PWA screen or i18n copy | apps/web/src/i18n/messages.ts, translation governance in AGENTS.md |
| Sprint execution policy | docs/automation/SPRINT_BATCH_AUTOPILOT.md, prompts/KAIRO_SPRINT_EXECUTOR.md |
| Product narrative or release history | PROJECT_STATUS.md (grep the section, do not read in full) |
| Historical rationale before Sprint 100 | IMPLEMENTATION_ROADMAP.md (grep a sprint section only) |
| Frozen Flutter behaviour reference | apps/flutter_kairo/AGENTS.md, docs/pwa/FLUTTER_TO_PWA_PARITY.md |

## Do not read at session start

| Path | Why |
| --- | --- |
| `IMPLEMENTATION_ROADMAP.md` | Historical Sprint 0-99 record. Grep one section; never read it in full. |
| `docs/flutter/**` | Frozen legacy client (ADR-014). Not part of the active program. |
| `orgmind_prompt_pack/**` | Historical prompt pack superseded by constitution/ and docs/architecture/. |
| `PROJECT_STATUS.md` | Long product narrative. Read the section a task names, not the file. |
| `.kairo/sprint-batch/handoffs/**` | Read only the handoff of the sprint being resumed. |
| `.kairo/sprint-batch/reports/**` | Audit trail. Read a report only when investigating a past failure. |

## Guard rails

The complete rules live in `AGENTS.md`. Non-negotiable subset:

- Every tenant-scoped query filters by `tenant_id`; the backend is the only policy enforcement point.
- LLMs never decide access control; retrieval filtering happens before prompt assembly.
- The frontend consumes API contracts only and duplicates no business rule.
- Never weaken a test, tolerance, security or authorization check to pass a gate.
- COMBIS is a demo tenant, never product logic.
- Roadmap V2 sprints are sequential: a blocked sprint blocks the batch; never skip ahead.

## Commands

| Intent | Command |
| --- | --- |
| Warm-up (static + live) | `npm run session:brief` |
| Regenerate this snapshot | `npm run session:brief -- --write` |
| Next unfinished sprint | `npm run sprint:next` |
| Batch status | `npm run sprint:batch:status` |
| Resume an incomplete batch | `npm run sprint:batch:resume` |
| Backend tests | `python -m pytest services/api/tests -q` |
| Web type check | `cd apps/web && npm run type-check` |
| OpenAPI + client contracts | `npm run contracts:check` |
| FR/EN/DE catalog parity | `node scripts/check-i18n-parity.mjs` |
| Hardcoded string scan | `node scripts/check-i18n-coverage.mjs` |
| PWA service worker guard | `npm run pwa:check` |
