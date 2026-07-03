# Project State

Last verified against repository code on 2026-07-02.

## Product Snapshot

Kairo, also positioned as OrgMind AI, is a local-first multi-tenant RAG platform for organizations.

The repository now enters a new professionalization track aimed at a mature association product with:

- read-only ordinary member surfaces
- role-specific office workspaces
- secure finance, sanctions, documents, and events governance
- a role-aware chatbot that never leaks cross-member data

## What Is Already Strong

- Multi-tenant authentication, tenant switching, session governance, and identity hardening
- Secure document RAG with citations, no-source refusal, prompt-injection defenses, structured chat boundaries, and audit traceability
- Membership, contributions, announcements, events, disciplinary records, document ingestion, and operational observability foundations
- Guided onboarding, role-aware dashboard progress, secretary workspace, treasurer finance workspace, auditor oversight, censor workspace, sports workspace, executive governance cockpit, principal-admin control plane, member-focused navigation simplification, and demo gallery
- Autonomous backend test posture with SQLite-first execution

## Main Gaps To Close

- Contribution reminder and collections follow-up automation are still missing for treasurer day-to-day operations
- Multi-tenant UX exists in the runtime, but reproducible multi-tenant provisioning and demo operations still lag behind the backend capability
- Backup, restore, and alert posture are documented, but first-class in-product operational evidence is still limited
- The chatbot now handles member balance and tenant finance-summary boundaries safely, but broader role-aware coverage for other approved domains still needs work

## Current Execution Plan

- Historical roadmap track completed: Sprint 41 through Sprint 52
- New post-release hardening track: Sprint 53 through Sprint 57
- Estimated additional sprints required from the current state: 4
- Next sprint: Sprint 54 - Member Renewal, Reminder, And Collections Automation

## Current State

- **Open-source release base**: strong and demonstrable
- **Roadmap status**: historical professional association maturity track completed; post-release hardening track reopened after the 2026-07-02 audit
- **Governance foundation**: canonical role catalog and backend capability matrix are now present
- **Authorization state**: the major backend modules now enforce explicit capabilities instead of broad inline role checks
- **Member self-service**: personal contribution history and member-only PDF statements are now in place
- **Secretary workspace**: a dedicated office workspace now exists for documents, policies, and announcements
- **Finance oversight**: treasurer operations and auditor read-only finance oversight now have distinct workspaces and backend permission checks
- **Executive oversight**: president and vice president now have a dedicated cross-module governance cockpit with limited, backend-governed actions
- **Principal admin control plane**: the broadest tenant administration surfaces now explicitly recognize `principal_admin` and show a dedicated control plane label
- **Member shell**: the ordinary member experience now keeps the sidebar compact and focused on personal essentials
- **Validation status**: targeted backend chat, prompt-safety, retrieval, and release-candidate matrix checks, plus frontend build and refreshed screenshot gallery generation, all passed on 2026-07-02
- **Commercial posture**: strong professional release candidate, usable for controlled self-hosted deployments but not yet a fully turnkey production offer
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
