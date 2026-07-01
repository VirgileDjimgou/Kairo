# Project State

Last verified against repository code on 2026-07-01.

## Product Snapshot

Kairo, also positioned as OrgMind AI, is a local-first multi-tenant RAG platform for organizations.

The repository now enters a new professionalization track aimed at a mature association product with:

- read-only ordinary member surfaces
- role-specific office workspaces
- secure finance, sanctions, documents, and events governance
- a role-aware chatbot that never leaks cross-member data

## What Is Already Strong

- Multi-tenant authentication, tenant switching, session governance, and identity hardening
- Secure document RAG with citations, no-source refusal, prompt-injection defenses, and audit traceability
- Membership, contributions, announcements, events, disciplinary records, document ingestion, and operational observability foundations
- Guided onboarding, role-aware dashboard progress, secretary workspace, treasurer finance workspace, auditor oversight, and demo gallery
- Autonomous backend test posture with SQLite-first execution

## Main Gaps To Close

- Backend capability enforcement is now in place across the major modules, but several role-specific workspaces still remain beyond the secretary and finance flows
- Dedicated workspaces do not yet exist for censor, sports manager, president, vice president, or principal administrator
- Office-role workspaces still need to be implemented over the new capability model
- The chatbot is secure for document retrieval, but not yet a full role-aware assistant over authorized structured association data

## Current Execution Plan

- New roadmap track: Sprint 41 through Sprint 52
- Estimated additional sprints required from the current state: 7
- Next sprint: Sprint 46 - Censor Discipline Workspace

## Current State

- **Open-source release base**: strong and demonstrable
- **Roadmap status**: active professional association maturity track, with Sprint 45 completed and Sprint 46 next
- **Governance foundation**: canonical role catalog and backend capability matrix are now present
- **Authorization state**: the major backend modules now enforce explicit capabilities instead of broad inline role checks
- **Member self-service**: personal contribution history and member-only PDF statements are now in place
- **Secretary workspace**: a dedicated office workspace now exists for documents, policies, and announcements
- **Finance oversight**: treasurer operations and auditor read-only finance oversight now have distinct workspaces and backend permission checks
- **Validation status**: targeted backend finance authorization tests, frontend build, and finance browser E2E all passed on 2026-07-01
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
