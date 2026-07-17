# Open-Source Release Readiness

This document captures the honest state of Kairo at the end of the stabilization
and open-source maturity track (Sprint 73). It is the reference for anyone who
wants to run, audit, or continue the project.

## What Is Verified

These statements reflect the repository as of 2026-07-16. Run the checks yourself
before trusting any claim.

| Area | Verified baseline |
|------|------------------|
| Backend tests | `python -m pytest services/api/tests -q` passes on SQLite (no PostgreSQL needed). 239 tests at last validation. |
| Frontend type-check | `npm run type-check` (vue-tsc) passes from `apps/web`. |
| Frontend build | `npm run build` produces a clean production bundle. |
| Localization E2E | `npm run test:e2e:locale` (Playwright, mocked API) passes on Chromium. |
| Role coverage | Member, secretary general, treasurer, auditor, censor, sports manager, president, vice president, and principal admin each have a dedicated, role-scoped workspace. |
| Tenant isolation | Every tenant-scoped query includes `tenant_id`; backend capability checks enforce access; frontend navigation is subordinate to backend authorization. |
| Chatbot safety | Retrieval filtering happens before prompt assembly; no-source refusal and prompt-injection guards are tested; the LLM never decides access control. |

## Open-Source Release Checklist

- [x] MIT `LICENSE` present at repository root.
- [x] `README.md` explains the product, architecture, quick start, demo credentials, and project structure.
- [x] `CONTRIBUTING.md` documents setup, conventions, tests, issue/PR reporting, and security disclosure.
- [x] `RELEASE_NOTES.md` summarizes audience, architecture, and known limits.
- [x] Backend test suite is autonomous (SQLite, no external infrastructure).
- [x] Frontend build and type-check are reproducible.
- [x] Deployment guide covers Docker Compose, reverse proxy, tunnel, backup/restore, and security checklist.
- [x] Role walkthrough references exist under `docs/demo-script.md` and `docs/github-demo/`.
- [x] Screenshot gallery under `docs/github-demo/role-gallery/` is generated from the current build.
- [x] Known limits and next-roadmap notes are explicit (this document).
- [ ] Live full-stack screenshots regenerated against the final seed on a clean host (reproducible via the existing capture scripts).

## Known Limits (Honest)

Kairo is a strong release candidate for disciplined self-hosting and pilot
deployments. It is not a finished commercial platform. The following limits are
real and should not be over-assumed:

- **Notification channels**: email is now wired for real identity delivery and
  for live operator dispatch from the notifications module when SMTP is
  configured. Telegram is now also wired for real operator dispatch when a bot
  token is configured. WhatsApp is now available through a simple gateway-backed
  operator path when a base URL and token are configured. A shared-secret
  callback seam now exists so trusted provider bridges can report final
  delivery outcomes back to the backend.
- **LLM dependency**: answers depend on a locally available model (Ollama or an
  OpenAI-compatible server such as LM Studio). No hosted LLM is bundled.
- **Identity delivery**: invite and password-reset messages need an SMTP
  provider to be delivered for real; otherwise they fall back to a simulated
  state that never exposes raw tokens.
- **Auth federation**: no SSO/SAML/OIDC integration yet.
- **Production packaging**: the production Docker path is validated through
  build and smoke checks, but a full multi-host production runbook is
  operational guidance, not a guaranteed certified deployment.
- **Mobile**: there is no native mobile app; the web UI is responsive.
- **Demo tenant**: the seeded demo tenant is fictional (Combis Sport Verein /
  demo slug) and must not be confused with a real organization or with product
  logic. COMBIS is never hardcoded as product behavior.
- **Tenant data in logs**: audit exports and chat traces are minimized, but
  operators should still review logging configuration before exposing the
  stack.

## Product Boundaries That Must Not Regress

- An ordinary member stays read-first: profile, balance, personal contribution
  history, and personal PDF statement only. A member never sees another member's
  financial, disciplinary, or personal data.
- Office roles get targeted write scopes by role (treasurer finances, secretary
  documents/policies/announcements, censor discipline, sports manager sports
  events, president/vice president governance oversight, auditor read-only
  finance, principal admin broadest tenant administration). No implicit global
  access.
- The backend is the only policy enforcement point. The frontend consumes API
  contracts only. The LLM never receives unauthorized chunks.

## Next Planning Cycle

After Sprint 73, the project leaves the foundational stabilization track. Future
work should start a new roadmap rather than extend Sprint 73. Candidate themes:

1. **Broader recovery UX**: extend the shared `useRecoveryState` contract to the
   remaining role workspaces (secretary, censor, sports, auditor, governance).
2. **Replay-safe reconciliation and polling**: harden the new callback seam
   with replay protection and add one controlled polling path so the live
   email, Telegram, and WhatsApp operator paths can keep progressing toward
   trustworthy final states when callbacks are unavailable or delayed.
3. **Operational dashboards**: package the existing `/metrics` and health
   signals into a reusable Grafana/Prometheus example.
4. **Auth federation**: evaluate OIDC/SAML for organizations that require SSO.
5. **Localization breadth**: the UI is French-first, English-second, German-third;
   additional locales would need i18n key coverage beyond the current 291 keys.

Contributors should read `docs/ai/NEXT_SPRINT.md` and `docs/ai/PROJECT_STATE.md`
for the most recent session handoff before starting new work.
