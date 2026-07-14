# Project State

Last verified against repository code on 2026-07-14.

## Product Snapshot

Kairo, demonstrated here as Combis Sport Verein, is a local-first multi-tenant RAG platform for organizations.

The repository now enters a new productization track aimed at a mature association product with:

- read-only ordinary member surfaces
- role-specific office workspaces
- secure finance, sanctions, documents, and events governance
- a role-aware chatbot that never leaks cross-member data

## What Is Already Strong

- Multi-tenant authentication, tenant switching, session governance, and identity hardening
- Secure document RAG with citations, no-source refusal, prompt-injection defenses, structured chat boundaries, and audit traceability
- Role-aware structured chat now covers member balances, tenant finance summaries, governance summaries, official publication context, disciplinary summaries, and sports schedules
- Configurable AI provider selection now supports Ollama or OpenAI-compatible local servers such as LM Studio
- Chat retrieval now rewrites queries before search and prefers same-language documents when available
- Streaming chat now returns citations in the final SSE payload and restores them when a conversation is reopened
- Browser chat streaming now targets the backend API directly, carries the bearer token, and commits new conversations before reuse
- Membership, contributions, announcements, events, disciplinary records, document ingestion, and operational observability foundations
- Guided onboarding, role-aware dashboard progress, secretary workspace, treasurer finance workspace with reminder automation, auditor oversight, censor workspace, sports workspace, executive governance cockpit, principal-admin control plane, member-focused navigation simplification, tenant operations command center, dashboard role-focus cards, demo gallery, and reproducible multi-tenant provisioning helpers
- Guided onboarding wizard, role-aware dashboard progress, secretary workspace, treasurer finance workspace with reminder automation, auditor oversight, censor workspace, sports workspace, executive governance cockpit, principal-admin control plane, member-focused navigation simplification, tenant operations command center, dashboard role-focus cards, demo gallery, and reproducible multi-tenant provisioning helpers
- Tenant-scoped recovery evidence surfaced through tenant settings, admin overview warnings, the new admin health center, and the settings page so backup and restore posture are visible in-product
- Autonomous backend test posture with SQLite-first execution

## Main Gaps To Close

- The historical sprint track is complete through Sprint 61, and Sprint 62 is now actively in progress

## Current Execution Plan

- Historical roadmap track completed: Sprint 41 through Sprint 52
- Post-release hardening track completed: Sprint 53 through Sprint 58
- New productization track planned: Sprint 62 through Sprint 64
- Estimated additional sprints required from the current state: 3
- Next sprint: Sprint 62 - Privacy, Audit, And Export Hardening

## Current State

- **Open-source release base**: strong and demonstrable
- **Roadmap status**: historical professional association maturity track completed; Sprint 62 is now in progress after the 2026-07-02 audit
- **Governance foundation**: canonical role catalog and backend capability matrix are now present
- **Authorization state**: the major backend modules now enforce explicit capabilities instead of broad inline role checks
- **Member self-service**: personal contribution history and member-only PDF statements are now in place
- **Secretary workspace**: a dedicated office workspace now exists for documents, policies, and announcements
- **Finance oversight**: treasurer operations and auditor read-only finance oversight now have distinct workspaces and backend permission checks
- **Collections automation**: treasurers can now send single-member and filtered reminder batches with backend-enforced notification delivery and reviewable reminder history
- **Executive oversight**: president and vice president now have a dedicated cross-module governance cockpit with limited, backend-governed actions
- **Principal admin control plane**: the broadest tenant administration surfaces now explicitly recognize `principal_admin` and show a dedicated control plane label
- **Member shell**: the ordinary member experience now keeps the sidebar compact and focused on personal essentials
- **Multi-tenant operations**: reproducible second-tenant provisioning, second-tenant captures, tenant-switch browser coverage, and the tenant operations command center now exist for live demo stacks
- **Validation status**: targeted backend reminder authorization tests, frontend build validation, finance browser regression coverage, Python seed helper import validation, tenant-switch browser coverage, backend recovery evidence tests, admin overview browser coverage, tenant operations browser coverage, release-candidate browser coverage, dashboard role-focus coverage, admin health center coverage, and onboarding wizard coverage passed on 2026-07-06
- **Localization and privacy stabilization**: the authenticated session now preserves the language chosen at login, member finance questions are recognized in French and German, cross-member finance requests are refused before the LLM, and fresh visual captures live under `apps/web/artifacts/manual-role-checks/2026-07-07/`
- **Privacy hardening status**: chat query traces now use minimized previews in the admin review surface, audit exports redact sensitive detail fields, and browser coverage verifies the minimized chat trace UI
- **Commercial posture**: strong professional release candidate, with a new productization track planned to move toward a more turnkey association deployment
- **Communications posture**: production-grade invite and password-reset delivery now uses tenant-aware provider context with explicit fallback handling
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

Then they should execute only the next planned sprint or the active sprint if one is already in progress.
