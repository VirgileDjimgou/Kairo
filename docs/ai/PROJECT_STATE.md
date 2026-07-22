# Project State

Last verified against repository code on 2026-07-21.

## Product Snapshot

Kairo, demonstrated here as Combis Sport Verein, is a local-first multi-tenant
RAG platform for organizations.

The repository now continues a productization track aimed at a mature
association product with:

- read-only ordinary member surfaces
- role-specific office workspaces
- secure finance, sanctions, documents, and events governance
- a role-aware chatbot that never leaks cross-member data

## What Is Already Strong

- Multi-tenant authentication, tenant switching, session governance, and identity hardening
- Secure document RAG with citations, no-source refusal, prompt-injection defenses, structured chat boundaries, and audit traceability
- Role-aware structured chat coverage for member balances, tenant finance summaries, governance summaries, publication context, disciplinary summaries, and sports schedules
- Guided onboarding, role-aware dashboard progress, secretary workspace, treasurer finance workspace, auditor oversight, censor workspace, sports workspace, governance cockpit, principal-admin control plane, and tenant operations command center
- Scripted production preflight, install, upgrade, rollback, backup, restore, and smoke-validation flows
- SQLite-first autonomous backend test posture
- Live notification operator delivery through SMTP-backed email, Telegram, and gateway-backed WhatsApp
- Tenant-scoped notification history with acceptance evidence, provider references, callback-based reconciliation, replay-safe polling support, and now backend-owned triage plus retry eligibility

## Main Gaps To Close

- Mypy now covers ALL 151 backend source files with zero errors — backend quality gates (ruff + mypy) are fully saturated
- Browser automation still covers only selected high-value journeys and can broaden carefully
- Some deeper frontend subflows may still need smaller parity cleanups beyond the dashboard-first pass completed in Sprint 87

## Current Execution Plan

- Historical roadmap track completed: Sprint 41 through Sprint 52
- Post-release hardening track completed: Sprint 53 through Sprint 58
- Productization track completed through Sprint 65
- Stabilization and open-source maturity track completed: Sprint 72 and Sprint 73
- New planning cycle status: Sprint 74 through Sprint 93 complete
- Next sprint: Sprint 94 - Role Journey Browser Coverage Expansion

## Current State

- **Open-source release base**: strong and demonstrable
- **Roadmap status**: Sprint 72 through Sprint 93 complete; Sprint 93 enabled exact optional-property and unchecked-index safeguards across the Vue application and corrected the affected client/store boundaries
- **Governance foundation**: canonical role catalog and backend capability matrix are present
- **Authorization state**: major backend modules enforce explicit capabilities instead of broad inline role checks
- **Member self-service**: personal contribution history and member-only PDF statements are in place
- **Secretary workspace**: dedicated office workspace exists for documents, policies, and announcements
- **Finance oversight**: treasurer operations and auditor read-only finance oversight have distinct workspaces and backend permission checks
- **Executive oversight**: president and vice president have a dedicated cross-module governance cockpit with limited, backend-governed actions
- **Principal admin control plane**: the broadest tenant administration surfaces recognize `principal_admin` explicitly
- **Multi-tenant operations**: reproducible second-tenant provisioning, tenant-switch browser coverage, and the tenant operations command center exist
- **Validation status**: `npm run type-check`, `npm run build`, and `npm run test:e2e:locale` (20 passed) passed on July 21, 2026 for Sprint 93; the backend quality gates remain fully covered through Sprint 92
- **Communications posture**: live notifications now support callback-updated final states, replay-safe updates, controlled provider polling, and backend-enforced retry eligibility without trusting the frontend
- **Commercial posture**: strong association-focused pilot and disciplined self-hosted release candidate
- **License**: MIT

## Continuity Rule

Future agent sessions should not invent the next step from memory.

They should read:

1. `README.md`
2. `AGENTS.md`
3. `constitution/KAIRO_CONSTITUTION.md`
4. `IMPLEMENTATION_ROADMAP.md`
5. `PROJECT_STATUS.md`
6. `prompts/CODEX_AUTOPILOT.md`
7. `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

Then they should execute only the next planned sprint or the active sprint if
one is already in progress.
