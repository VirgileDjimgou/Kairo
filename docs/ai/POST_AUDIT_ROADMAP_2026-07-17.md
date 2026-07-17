# Post-Audit Roadmap Extension — 2026-07-17

This roadmap extends the current Kairo delivery track after Sprint 85.

It is intentionally limited to eight dense sprints so the team can close the
main audit weaknesses without re-opening the product scope too broadly.

## Planning Principles

- Preserve backend-owned authorization and tenant isolation
- Prefer vertical slices over broad refactors
- Expand validation before adding wide new feature surface
- Improve operator maturity only where the product already has a proven base
- Keep ordinary members on a simple read-first experience

## Sprint 86 — Notification Reconciliation Operations And Stale-Delivery Triage

**Objectif :**
Turn the new replay-safe and pollable reconciliation seam into a usable operator
workflow for pending and failed deliveries.

**Problèmes résolus :**

- Notification history is still too flat for real follow-up
- Pending deliveries require manual interpretation
- Failed deliveries do not yet have a clear triage path

**Tâches principales :**

- Add server-side filters and summary counts for pending, delivered, and failed notification history
- Add safe retry eligibility rules enforced in the backend
- Add operator-visible stale-delivery age cues
- Extend audit entries so retries and poll refreshes remain traceable

**Composants concernés :**

- `services/api/app/modules/notifications/*`
- `apps/web/src/views/admin/AdminNotificationsView.vue`
- notification provider abstractions and tests

**Dépendances :**

- Sprint 85 completed

**Tests requis :**

- Backend tests for filter, retry eligibility, and retry audit evidence
- Frontend type-check and build
- Browser coverage for pending and failed triage flows

**Critères d’acceptation :**

- An operator can isolate stale pending deliveries quickly
- Retry remains impossible when backend rules do not allow it
- No cross-tenant or cross-role leakage appears in triage or retry flows

**Livrable démontrable :**

- Admin notifications workspace with clear triage and retry-safe flows

**Risques et rollback :**

- Risk: retry logic could duplicate real sends
- Rollback: keep retry behind explicit backend eligibility and feature-gate any provider-specific resend

**Estimation :** M

## Sprint 87 — Frontend Role Parity And Workspace Entry Contract

**Objectif :**
Align frontend navigation, dashboard entry points, and role visibility with the
backend capability model already in place.

**Problèmes résolus :**

- Frontend role discoverability still lags behind backend capability granularity
- Users can have a correct permission model but an unclear workspace experience

**Tâches principales :**

- Define a canonical frontend capability-to-workspace map
- Remove residual over-broad or ambiguous navigation states
- Add consistent role-specific quick actions and empty states
- Audit sensitive route visibility against backend authorization behavior

**Composants concernés :**

- `apps/web/src/router`
- dashboard, layouts, role workspaces, auth bootstrap stores
- targeted backend authorization tests where gaps appear

**Dépendances :**

- existing capability matrix and role workspaces

**Tests requis :**

- Frontend role-routing tests
- Playwright role-entry checks
- Backend denial-path tests for mismatched UI assumptions

**Critères d’acceptation :**

- Every target role sees only the right primary workspaces
- No sensitive route is presented as available when backend denies it
- Member experience stays compact and read-first

**Livrable démontrable :**

- Clean role-by-role navigation parity across member and office sessions

**Risques et rollback :**

- Risk: hiding a route could reduce discoverability for a legitimate role
- Rollback: keep capability mapping centralized and revert only the affected entry points

**Estimation :** M

## Sprint 88 — Chat Authorization Surface And Domain Guard Expansion

**Objectif :**
Broaden role-aware chatbot coverage only where the backend can guarantee safe
structured access boundaries.

**Problèmes résolus :**

- Chat is strong on some domains but still uneven across the full association role matrix
- New role surfaces can outpace explicit prompt and retrieval guard coverage

**Tâches principales :**

- Review each role/domain pair for allowed, refused, and source-bound behavior
- Centralize more chat domain policies in backend-readable contracts
- Extend refusal and structured-summary tests for governance, discipline, and operations questions
- Keep forbidden cross-member private data outside prompt assembly and logs

**Composants concernés :**

- `services/api/app/modules/chat/*`
- `services/api/app/modules/rag/*`
- chat tests and policy tests

**Dépendances :**

- Sprint 87 role-entry parity

**Tests requis :**

- Backend chat safety regressions per role
- Retrieval-boundary tests
- Stream and non-stream parity checks

**Critères d’acceptation :**

- Each approved role gets useful chatbot coverage only on authorized domains
- Cross-member private finance, sanctions, and private documents remain refused
- Prompt assembly never receives unauthorized data

**Livrable démontrable :**

- Expanded role-safe chat coverage matrix with regression evidence

**Risques et rollback :**

- Risk: over-expanding chat scope creates silent privacy regressions
- Rollback: keep policy decisions centralized and revert by domain contract

**Estimation :** M

## Sprint 89 — Quality Gate Expansion And CI Hardening

**Objectif :**
Move from partial validation subsets toward a stronger automated non-regression baseline.

**Problèmes résolus :**

- Ruff and Mypy are still scoped to small backend subsets
- Browser automation covers only a narrow pack in CI

**Tâches principales :**

- Expand Ruff coverage module by module
- Expand Mypy scope where typing debt is already manageable
- Add one or two additional browser packs for critical role journeys
- Document a quality-gate escalation strategy so CI grows without destabilizing delivery

**Composants concernés :**

- `.github/workflows/ci.yml`
- `services/api/pyproject.toml`
- backend typing targets
- frontend browser specs

**Dépendances :**

- Sprint 87 and Sprint 88 reduce ambiguity in role and chat surfaces

**Tests requis :**

- CI dry-run locally where possible
- expanded lint, type, backend, and browser commands

**Critères d’acceptation :**

- CI validates a broader, meaningful subset of the product
- New failures are actionable, not noisy or random
- Delivery remains reproducible on contributor machines

**Livrable démontrable :**

- Stronger CI matrix with updated validation docs

**Risques et rollback :**

- Risk: gate expansion blocks delivery on legacy debt
- Rollback: graduate modules progressively instead of enforcing full strictness at once

**Estimation :** M

## Sprint 90 — Critical End-To-End Journeys And Demo Seed Reliability

**Objectif :**
Turn the strongest role journeys into reproducible end-to-end evidence on a seeded stack.

**Problèmes résolus :**

- Many critical flows are validated in parts, not consistently end to end
- Demo confidence is high, but regression evidence is still fragmented

**Tâches principales :**

- Add repeatable seeded-stack E2E coverage for member, treasurer, secretary, principal admin, and tenant switching
- Stabilize seed assumptions and browser helpers
- Capture deterministic smoke evidence for the most important journeys

**Composants concernés :**

- `apps/web/e2e/*`
- seed scripts
- browser capture utilities

**Dépendances :**

- Sprint 87 role parity
- Sprint 89 stronger quality gates

**Tests requis :**

- Full seeded-stack browser runs on critical journeys
- targeted seed-validation checks

**Critères d’acceptation :**

- Core role journeys can be replayed reliably on the seeded environment
- Demo regressions are caught before manual showcase time

**Livrable démontrable :**

- One reproducible E2E pack for the main association operating flows

**Risques et rollback :**

- Risk: E2E flakiness burns time and confidence
- Rollback: keep critical pack short and deterministic before broadening it

**Estimation :** M

## Sprint 91 — Production Pipeline Fidelity And Release Proof

**Objectif :**
Raise production confidence from good documentation to repeatable build and smoke evidence.

**Problèmes résolus :**

- Production path is documented, but CI does not yet prove the whole release chain
- Operator confidence still depends on manual packaging validation

**Tâches principales :**

- Add production Docker build validation in CI
- Add smoke verification against the production-shaped stack
- Review environment contract drift between local, test, and production files
- Add a release checklist artifact that points only to verified commands

**Composants concernés :**

- `.github/workflows/ci.yml`
- Dockerfiles
- compose files
- deployment and operations docs

**Dépendances :**

- Sprint 89 validation maturity

**Tests requis :**

- CI production build
- smoke script validation
- configuration render validation

**Critères d’acceptation :**

- Production-shaped build artifacts are validated automatically
- Release instructions match what CI actually proves

**Livrable démontrable :**

- CI-backed production packaging proof

**Risques et rollback :**

- Risk: production CI adds runtime and maintenance cost
- Rollback: keep smoke stack minimal and focused on build fidelity first

**Estimation :** M

## Sprint 92 — Privacy Operations, Retention, And Governance Layer

**Objectif :**
Make data-governance operations more explicit for a real association or NGO context.

**Problèmes résolus :**

- Privacy and compliance posture is technically strong but still under-productized
- Boards and operators need clearer governance actions around export, retention, and deletion

**Tâches principales :**

- Define explicit retention and archival rules for sensitive records
- Add safe export and deletion governance paths where appropriate
- Review audit minimization and sensitive-field exposure
- Document professional review points for GDPR-adjacent operations

**Composants concernés :**

- identity, audit, membership, contributions, disciplinary, documents
- admin settings or governance surfaces
- compliance-facing docs

**Dépendances :**

- Sprint 88 chat guard maturity
- Sprint 91 release confidence

**Tests requis :**

- Backend tests for export/deletion authorization and audit behavior
- targeted UI validation for governance actions

**Critères d’acceptation :**

- Sensitive governance operations are explicit, auditable, and backend-enforced
- The product is clearer about what is automated and what still needs professional review

**Livrable démontrable :**

- Admin governance flows and docs for privacy-sensitive operations

**Risques et rollback :**

- Risk: over-engineering compliance before real field feedback
- Rollback: ship explicit minimum governance operations only

**Estimation :** L

## Sprint 93 — Commercial Narrowing And Pilot Packaging

**Objectif :**
Turn the mature technical base into a sharper pilot-ready product package for the most credible niche.

**Problèmes résolus :**

- The product is broad and impressive, but positioning can still diffuse attention
- Technical strength is ahead of commercial narrowing

**Tâches principales :**

- Pick one primary association segment and one secondary segment
- Align offer pack, feature matrix, onboarding, and demo narrative to that focus
- Separate “pilot-ready now” from “roadmap later”
- Define a tighter three-offer packaging model backed by current capabilities

**Composants concernés :**

- commercial docs
- README product framing
- demo and onboarding material

**Dépendances :**

- Sprint 90 demo reliability
- Sprint 91 production evidence
- Sprint 92 governance clarity

**Tests requis :**

- Document consistency review
- live demo path review against actual product surface

**Critères d’acceptation :**

- The product has one clear commercial story
- The documented offer does not promise more than the repo proves

**Livrable démontrable :**

- Sharpened pilot package and buyer-facing positioning

**Risques et rollback :**

- Risk: commercial narrowing hides real platform flexibility
- Rollback: keep secondary segments documented separately from the primary go-to-market story

**Estimation :** M
