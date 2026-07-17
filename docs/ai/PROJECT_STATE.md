# Project State

Last verified against repository code on 2026-07-16.

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
- Tenant-scoped recovery evidence surfaced through tenant settings, admin overview warnings, the new admin health center, and the settings page so backup and restore posture are visible in-product
- Scripted production preflight, install, upgrade, rollback, backup, restore, and smoke-validation flows now exist for the self-hosted packaging path
- Autonomous backend test posture with SQLite-first execution

## Main Gaps To Close

- French-first UI coverage is now complete across all primary admin, finance, and workspace views with 291 i18n keys and governance rules in AGENTS.md
- Validation guardrails now exist again, but the current Ruff and Mypy baselines are intentionally scoped and should expand as more legacy modules are cleaned
- Chat orchestration has started to split into prompt and payload seams, but retrieval and policy evaluation can still be decomposed further later
- The main remaining productization gap in the current module set is hardening notification reconciliation with replay safety and a controlled polling fallback for providers that do not push reliable callbacks

## Current Execution Plan

- Historical roadmap track completed: Sprint 41 through Sprint 52
- Post-release hardening track completed: Sprint 53 through Sprint 58
- Productization track completed through Sprint 65
- Stabilization and open-source maturity track completed: Sprint 72 and Sprint 73 done
- New planning cycle started: Sprint 74 through Sprint 84 complete; the next candidate themes from `docs/OPEN_SOURCE_RELEASE.md` now continue from the now-expanded live notification baseline
- Estimated additional sprints required from the current state: 0 for the stabilization track; the new planning cycle now moves from recovery UX plus the first real notification channel to the next productization theme
- Next sprint: `Sprint 85 - Notification Reconciliation Polling And Replay-Safety Baseline`

## Current State

- **Open-source release base**: strong and demonstrable
- **Roadmap status**: historical professional association maturity track completed; Sprint 72, Sprint 73, Sprint 74, Sprint 75, Sprint 76, Sprint 77, Sprint 78, Sprint 79, Sprint 80, Sprint 81, Sprint 82, Sprint 83, and Sprint 84 done; Sprint 74 through Sprint 78 completed the currently identified broader recovery UX rollout, Sprint 79 added the first real notification-channel increment, Sprint 80 packaged the current observability surface into a reusable operator baseline, Sprint 81 added Telegram as a second real operator-usable notification channel, Sprint 82 added a gateway-backed WhatsApp live path, Sprint 83 added audited delivery-stage evidence plus a tenant-scoped notification history baseline, and Sprint 84 added a secure callback seam plus final-state history merging
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
- **Validation status**: the repository-root backend suite (`python -m pytest services/api/tests -q`), scoped Ruff baseline, scoped Mypy baseline, frontend type-check/build, and the localization Playwright pack all passed on 2026-07-15; warnings remain in a few legacy tests and external-service probes, but the documented quality gates are now reproducible
- **Deployment packaging status**: production packaging now has shared operations helpers plus guided install, upgrade, rollback, and smoke-check scripts aligned with the actual gateway surface
- **Commercial packaging status**: offer pack, buyer FAQ, support boundary, feature matrix, and handoff-facing commercial docs are now synchronized with the verified runtime surface
- **Localization and privacy stabilization**: the authenticated session now preserves the language chosen at login, member finance questions are recognized in French and German, cross-member finance requests are refused before the LLM, and fresh visual captures live under `apps/web/artifacts/manual-role-checks/2026-07-07/`
- **Sprint 66 hardening**: privileged document-access parity now covers both `admin` and `principal_admin`, the admin settings language contract is restricted to FR/EN/DE, and the tenant settings plus admin documents surfaces now follow the active session language
- **Sprint 67 translation governance**: all primary admin, finance, and workspace views (members, contributions, events, policies, disciplinary, finance, auditor, censor) now use centralized i18n keys from `messages.ts` with French-first, English-second, German-third coverage; 291 unique i18n keys now in the dictionary; translation governance rules documented in AGENTS.md; automated coverage check script at `scripts/check-i18n-coverage.mjs`
- **Sprint 68 validation recovery**: the backend suite now runs from the repository root, Playwright has a cross-platform web-server launcher, `apps/web/package.json` exposes the selected browser pack, and `docs/operations/validation-baseline.md` captures the active backend/frontend/browser commands
- **Sprint 69 chat modularization**: prompt assembly and retrieval-query shaping now live in `services/api/app/modules/chat/prompting.py`, citation/context payload helpers now live in `services/api/app/modules/chat/payloads.py`, `query` and `query-stream` share one preparation path, and stream responses now refuse no-source questions before the LLM just like the non-streaming path
- **Sprint 70 document metadata hardening**: uploads no longer default blindly to English, archive imports now share centralized backend language inference plus conservative finance/governance/disciplinary classification, and multilingual regression coverage now protects FR/EN/DE plus ambiguous-language fallback to `und`
- **Sprint 71 retrieval maturity**: the shipped retrieval contract is now explicit as dense search plus lexical keyword boosting, language-aware ordering, and optional reranking; backend logs now summarize retrieval mode and candidate counts; targeted ranking regressions cover the supported strategy
- **Sprint 72 recovery polish**: member self-service and treasurer finance workspaces now share a `useRecoveryState` contract with a localized retry control and privacy-safe recovery hint; frontend build, type-check, and an autonomous Playwright recovery test pass
- **Sprint 73 open-source readiness**: `docs/OPEN_SOURCE_RELEASE.md` records the verified baseline (239 backend tests, type-check, build, E2E), an honest known-limits list, and non-regression boundaries; `CONTRIBUTING.md` and `RELEASE_NOTES.md` refreshed; the stabilization track is closed and future work starts a new planning cycle
- **Sprint 74 broader recovery UX**: the Censor and Sports workspaces now share the `useRecoveryState` contract with the standard recovery alert and localized retry control; `censor.workspaceErrorTitle` and `sports.workspaceErrorTitle` added across FR/EN/DE; new E2E recovery tests for both workspaces pass; frontend build, type-check, and 9 E2E tests green
- **Sprint 75 broader recovery UX**: the Auditor workspace and Governance cockpit now share the same `useRecoveryState` recovery contract with localized workspace error titles, recovery hints, and retry controls; `auditor.workspaceErrorTitle` and `governance.workspaceErrorTitle` added across FR/EN/DE; localization E2E now covers 11 passing recovery-and-language scenarios
- **Sprint 76 broader recovery UX**: the secretary document workspace and the principal-admin overview now share the same `useRecoveryState` recovery contract with localized workspace error titles, recovery hints, and retry controls; localization E2E now covers 13 passing recovery-and-language scenarios
- **Sprint 77 broader recovery UX**: the secretary announcements workspace and the tenant operations command center now share the same `useRecoveryState` recovery contract with localized workspace error titles, recovery hints, and retry controls; localized action errors remain separate for mutations and tenant switching; localization E2E now covers 15 passing recovery-and-language scenarios
- **Sprint 78 broader recovery UX**: the secretary policy workspace, admin health center, onboarding wizard, and tenant settings now share the same `useRecoveryState` recovery contract with localized workspace error titles, recovery hints, and retry controls; localized action/save errors remain separate where needed; localization E2E now covers 19 passing recovery-and-language scenarios
- **Sprint 79 notification baseline**: the notifications module now exposes one real operator-usable channel through SMTP-backed email dispatch with backend-owned capability checks, audit logging, a localized admin console that distinguishes live from simulated delivery, backend notification tests (8 passing), and localization E2E now covering 20 passing scenarios
- **Sprint 80 observability packaging**: the repository now ships a versioned `infra/monitoring/` package with Prometheus and Grafana baselines, a reusable `Kairo Operator Overview` dashboard, an operations guide for startup plus metric mapping, and a backend regression test that ensures the packaged dashboard stays aligned with the actual `/metrics` contract
- **Sprint 81 broader real notifications**: the notifications module now supports live operator delivery through SMTP-backed email and Telegram, the admin notifications workspace now presents multiple live-capable channels honestly, backend notification coverage now includes Telegram provider behavior plus tenant-admin and principal-admin live dispatch, and localization E2E still covers 20 passing scenarios after the multi-channel update
- **Sprint 82 WhatsApp baseline**: the notifications module now supports a third live operator path through a gateway-backed WhatsApp provider, the admin notifications workspace now reflects all three live-capable channels honestly, backend notification coverage now includes the WhatsApp provider plus tenant-admin and principal-admin live dispatch, and localization E2E remains green after the full multi-channel update
- **Sprint 83 notification reconciliation baseline**: the notifications module now returns backend-owned delivery-stage and reconciliation metadata, persists provider references when available, exposes a tenant-scoped audited history endpoint for operator review, and keeps the admin notifications workspace synchronized to backend audit evidence instead of local-only result state
- **Sprint 84 notification callback baseline**: the notifications module now exposes a shared-secret provider callback endpoint, correlates final-state updates by tenant, channel, and provider reference, rejects invalid callback tokens, and merges confirmed delivered or failed states back into the operator history surface
- **Privacy hardening status**: chat query traces now use minimized previews in the admin review surface, audit exports redact sensitive detail fields, and browser coverage verifies the minimized chat trace UI
- **Commercial posture**: strong association-focused pilot and disciplined self-hosted release candidate, now being hardened toward a stable open-source release
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
