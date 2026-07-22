# Project Status

Last updated: 2026-07-22

## Current Sprint

Sprint 97 - Production Docker Evidence And Handoff Validation

Status: Completed

## Official Next Sprint

Sprint 98 - Operational Pilot Acceptance

Status: In Progress - External pilot inputs required

## Active Delivery Frame

- Target outcome: a stable, professional, mature open-source association-management product with secure role-aware workspaces and a trustworthy chatbot
- Intended operational scope: usable by an association or organization of about 200 members with differentiated office roles
- Remaining planned execution window: 1
- Delivery status: Sprint 98 added a non-disclosing pilot preflight; the local development environment correctly fails it until real pilot secrets, HTTPS exposure, and restore-drill inputs exist. It also provides a PowerShell Quick Tunnel demonstration helper that uses temporary web/API-only exposure without a Cloudflare account, domain, token, or edits to `.env`; it is explicitly not a production path.

## Source Of Truth

- Constitution: `constitution/KAIRO_CONSTITUTION.md`
- Deep product docs: `orgmind_prompt_pack/`
- Roadmap: `IMPLEMENTATION_ROADMAP.md`
- Autopilot prompt: `prompts/CODEX_AUTOPILOT.md`

## Professionalization Assessment

- Estimated additional sprints required from the current state: 1
- Current strengths:
  - multi-tenant auth and role resolution
  - secure document RAG with citations and prompt-injection defenses
  - role-aware structured chat boundaries for member balances, tenant finance summaries, governance summaries, publication context, disciplinary summaries, and sports schedules
  - membership, contributions, events, announcements, disciplinary, audit, and onboarding foundations
  - dedicated secretary, treasurer, auditor, censor, sports, executive governance, and principal admin workspaces
  - role-specific navigation simplification for members and office roles, including member PDF statements
  - backend-owned chat domain policy exposure that now keeps publication, sports, governance, disciplinary, personal finance, and tenant-finance assistant surfaces aligned with real tenant module availability
  - treasurer-safe reminder history and collections follow-up workflows tied directly to contribution records
  - autonomous test posture and role-aware dashboard, secretary, finance, sports, governance, and principal-admin improvements
  - refined dashboard workspace focus cards that point each role to the right workspace immediately, with frontend-visible entry points now brought back into parity with actually allowed routes
  - dedicated admin health center that combines live dependency checks with tenant recovery evidence and now follows the shared recovery alert pattern
  - dedicated onboarding wizard that provides a concise first-run setup path and demo seed guidance and now follows the shared recovery alert pattern
  - tenant operations command center with explicit membership inventory, current-tenant posture, and confirmation-based tenant switching
  - production-grade invite and password-reset delivery with tenant-aware provider context and explicit fallback handling
  - admin notification extensions console now distinguishes simulation from live delivery and can send a real SMTP-backed operator email, Telegram message, or gateway-backed WhatsApp message when configured
  - notification dispatch responses and the admin notification console now expose backend-owned delivery-stage evidence, reconciliation status, provider references when available, and a tenant-scoped audited history endpoint
  - the notification module now accepts backend-owned provider reconciliation callbacks through a shared-secret endpoint, correlates them to live dispatches by tenant and provider reference, and updates operator history toward final delivered or failed states
  - the admin notifications workspace now exposes backend-owned triage summaries, filtered history, stale-pending cues, and safe retry actions for eligible failed deliveries only
  - release-candidate regression matrix, professional handoff checklist, and a reproducible role-and-tenant screenshot gallery
  - French-first interface foundation with persistent user language preference and English/German alternates
  - recovered validation baseline with root-level backend test execution, a portable Playwright browser pack, a scoped Ruff guardrail, and an operational initial Mypy target
  - modularized chat seams for prompt assembly, retrieval-query shaping, citation/context payload assembly, and shared query/query-stream preparation
  - configurable AI provider selection for Ollama or OpenAI-compatible local servers such as LM Studio
  - retrieval query rewriting that expands multilingual search hints before vector lookup
  - streaming chat citation persistence and restored citations when reopening a conversation
  - direct-backend SSE chat streaming from the browser, with authenticated fetches and committed conversation creation
  - Combis Sport Verein demo branding and a larger fictional member roster aligned with the association use case
  - language-aware chat requests plus a safer archive import base for the provided association documents
  - normalized document-language inference for uploads and archive imports, with conservative archive sensitivity classification for finance, governance, and disciplinary material
  - explicit dense retrieval with lexical keyword boosting, language-aware ordering, optional reranking, and structured retrieval observability for chat flows
  - explicit privileged document-access parity now covers both the legacy `admin` role and the canonical `principal_admin` role for RAG/document policy enforcement
  - tenant settings, onboarding, health, policy, and admin document surfaces now respect the active FR, EN, or DE session language and keep a consistent retry-oriented recovery flow
  - scripted production preflight, install, upgrade, backup, restore, rollback, and smoke-validation workflows for self-hosted operators
  - production packaging now proxies `/metrics` explicitly and blocks `/docs`, `/redoc`, and `/openapi.json` on the public gateway surface
  - packaged Prometheus and Grafana monitoring assets now exist under `infra/monitoring/`, with a regression guard that keeps the bundled dashboard aligned to the actual `/metrics` contract
  - commercial offer pack, buyer FAQ, support-boundary guidance, and first-contact commercial reading order
  - post-Sprint-63 stabilization now keeps the login language choice across the authenticated session, extends chat finance/privacy guards to French and German phrasing, and includes refreshed role screenshots under `apps/web/artifacts/manual-role-checks/2026-07-07/`
- Main gaps before the target product is mature:
  - notification triage is now clearer, but the broader frontend role-entry contract still needs parity work so each role sees only the right primary workspaces and routes
  - chat orchestration is now safer to extend, but the newer seams still need broader rollout if we later split retrieval and policy evaluation further
  - backup, restore, and alert posture are now visible in-product through the new health center and settings surfaces
  - deployment packaging and commercial handoff are now documented, while archive-import validation evidence and any future positioning changes should be treated as a new planning cycle

## Production Verdict

- Kairo is usable as a controlled production release candidate for disciplined self-hosting or pilot deployments.
- Kairo remains a strong association-focused pilot and disciplined self-hosted release candidate.
- The next planned track completes customer-facing pilot acceptance with real secrets, a real domain or tunnel, and backup/restore evidence before any new product-surface work.

## Completed

- Completed Sprint 0 foundation and repository skeleton.
- Completed Sprint 1 identity, tenancy, and JWT authentication.
- Completed Sprint 2 professional Vue layout.
- Completed Sprint 3 document upload and object storage.
- Completed Sprint 4 ingestion worker and parsing.
- Completed Sprint 5 embeddings and Qdrant indexing.
- Completed Sprint 6 first RAG chat, including secure retrieval, citations, refusal behavior, and chat trace logging.
- Completed Sprint 7 admin RAG controls, including document access management, reindexing, and chat traceability.
- Completed Sprint 8 membership and contributions module, including:
  - MembershipProfile, ContributionRecord, and PaymentRecord ORM models
  - Full REST API for CRUD operations on member profiles
  - Contribution management with automatic balance calculation
  - Payment recording with automatic balance updates
  - Tenant-isolated queries for all membership and contribution operations
  - Contribution summary endpoint (aggregate expected/paid/balance per year)
  - Member self-view (profile + balance) and admin management views
  - Full integration test suite (11 tests) covering tenant isolation, balance calculation, payment recording, and CRUD
- Completed Sprint 9 policies, rules, and discipline module, including:
  - PolicyRecord and DisciplinaryRecord ORM models
  - Public policy browsing and tenant policy catalog endpoints
  - Admin policy CRUD with category tracking and document linkage
  - Private disciplinary record access for members
  - Admin/treasurer disciplinary management with role-based controls
  - Frontend policy and disciplinary views for member and admin surfaces
  - Backend integration tests covering visibility, isolation, and staff permissions
- Completed Sprint 10 events and announcements module, including:
  - Event and Announcement ORM models with visibility scopes and status tracking
  - Full REST API for tenant-scoped event CRUD (admin) and public listing (members)
  - Full REST API for tenant-scoped announcement CRUD (admin) and active listing (members)
  - Visibility scope filtering: members see only non-admin_only published content
  - Active announcement filtering by published_at/expires_at
  - Admin-only enforcement on create/update/delete endpoints
  - Tenant isolation on all queries
  - Frontend EventsView and AnnouncementsView for member surface
  - Frontend AdminEventsView and AdminAnnouncementsView for admin management
  - Admin sidebar navigation links for Events and Announcements
  - Member sidebar navigation links for Events and Announcements
  - Backend integration tests: 13 tests covering CRUD, visibility, isolation, admin enforcement, and date filtering
- Completed Sprint 11 Cloudflare Tunnel Deployment, including:
  - production nginx.conf for frontend Dockerfile (was missing, now builds correctly)
  - docker-compose.prod.yml override for production targets (2 workers, no debug, no volume mounts)
  - .env.production.example with hardened security defaults and documentation
  - Enhanced cloudflare tunnel config sample with setup instructions and security rules
  - Caddy reverse proxy config sample (Caddyfile) with SPA fallback, API proxy, and security headers
  - Caddy docker-compose include file for easy deployment alongside the stack
  - backup.sh script for all persistent volumes (PostgreSQL dump, Redis, Qdrant, MinIO, Ollama)
  - Comprehensive deployment guide (docs/deployment-guide.md) covering architecture, setup, environment,
    reverse proxy, Cloudflare Tunnel, backup/restore, security checklist, and troubleshooting
- Completed Sprint 12 Evaluation and AI Safety, including:
  - Hardened system prompt with untrusted source boundary (<sources> tags, anti-injection rules)
  - Prompt injection tests (5 tests): verify injection guards in prompts, source demarcation, access
    control still enforced for injection documents, no-source refusal after hardening, admin-only
    documents hidden from members even with injection content
  - Retrieval evaluation and answer quality tests (4 tests): citations returned with sources, excerpts
    contain source text, top_k limits citations, confidence non-zero when sources found
  - Enhanced admin audit review screen with search by question text, status filter (all/answered/refused),
    configurable result limit, and summary statistics cards
- Completed Sprint 13 Demo Tenant and Portfolio Polish, including:
  - Enhanced seed script with comprehensive demo tenant data (Acme Community Organization - anonymized, not COMBIS)
  - 4 demo users: admin, 2 members (Alice, Bob), treasurer (Carol)
  - 3 granular roles with permission assignments (admin, member, treasurer)
  - Membership profiles, contributions with payments, disciplinary records
  - Sample policies linked to documents, sample events and announcements with visibility scoping
  - Documents with versions and chunks for RAG retrieval
  - Updated README, demo walkthrough, and seed helper scripts
- Completed Sprint 14 Multi-Channel Extensions, including:
  - Notification provider abstraction isolated from the core web product flow
  - Optional Email, Telegram, and WhatsApp placeholder providers
  - Admin-only notification channel diagnostics endpoint
  - Admin-only simulated notification dispatch endpoint
  - Admin notification extensions console in the Vue frontend
  - Integration tests covering admin enforcement, provider discovery, and simulated dispatch
- Completed Sprint 15 Commercialization Baseline, including:
  - Tenant settings API (GET/PUT /api/v1/tenants/{id}/settings) with branding and module toggle CRUD
  - Module toggle utility with 8 known modules (membership, contributions, policies, disciplinary, events, announcements, chat, notifications) — all default-enabled
  - Admin-only enforcement on settings update endpoint
  - Enhanced /health endpoint returning available module list
  - Vue frontend admin settings page with organization info, branding (color picker), and module toggle checkboxes
  - MIT LICENSE file added
  - Default module toggles in seed.py demo tenant
  - 86 backend tests pass, 0 failures
- Completed Sprint 16 Tenant Activation And Multi-Tenant UX, including:
  - API-driven tenant membership loading replacing hardcoded frontend placeholder tenants
  - Enriched `/auth/me` endpoint returning memberships with branding and module toggles
  - `/auth/switch-tenant` endpoint for JWT re-issuance across tenant boundaries
  - Multi-tenant login flow with post-login tenant picker for users with multiple organizations
  - Tenant branding (primary color) applied across AppLayout and AdminLayout
  - Module-aware navigation filtering based on tenant module toggle settings
  - Real API-backed tenant switcher in the member layout
  - 5 new backend integration tests (91 total), 0 failures
  - Frontend builds clean (206 modules)
- Completed Sprint 18 Module Enforcement And Entitlements, including:
  - Reusable `require_module(module_key)` FastAPI dependency factory in `app/core/module_guard.py`
  - Router-level enforcement on all 8 module routers: membership, contributions, policies, disciplinary, events, announcements, chat, notifications
  - Consistent 403 response with module name in detail for disabled modules
  - Inline module check on admin router's `/admin/chat-queries` endpoint
  - Admin settings UX warning before disabling modules with existing data (GET `/admin/module-has-data` endpoint)
  - Frontend route-level module guard in `router.beforeEach` checking `meta.module` against tenant store
  - 6 new backend tests covering disabled/enabled states for all guarded modules
  - 119 total backend tests, 0 failures
- Completed Sprint 19 Audit Trail and Administrative Governance, including:
  - Audit event model, repository, service, and admin review/export routes
  - Backend audit logging for tenant settings, documents, memberships, contributions, events, announcements,
    disciplinary records, invitations, MFA changes, and notification tests
  - Frontend admin audit trail screen with filters, summary cards, and CSV export
  - Audit isolation tests and export validation
  - 121 total backend tests, 0 failures
- Completed Sprint 20 Document Operations Maturity, including:
  - Real OCR parsing for image documents through the image OCR parser
  - Bulk document upload with partial success reporting
  - Duplicate detection baseline using checksum plus filename heuristics
  - Archive/unarchive lifecycle actions for documents
  - Retry action for failed ingestion jobs
  - Document lifecycle tests covering OCR, bulk upload, archive/restore, and retry flows
  - Frontend admin documents UI actions for bulk upload, archive, restore, and retry
- Completed Sprint 21 Data Import And Backoffice Automation, including:
  - Shared CSV import/export utility (`app/core/import_export.py`) with parse/generate functions and `ImportResult` schema
  - Member CSV import with dry-run mode, field validation, duplicate detection, and tenant isolation
  - Contribution CSV import with dry-run mode, member-code resolution, field validation, and tenant isolation
  - Export endpoints for members, contributions, events, and announcements using `StreamingResponse`
  - Admin frontend import modals with CSV file upload, dry-run checkbox, validation summary table, and confirm-import flow
  - Admin frontend export buttons for members, contributions, events, and announcements
  - 19 new backend integration tests covering CSV parsing, import validation, export correctness, admin enforcement, and tenant safety
  - 144 total backend tests, 0 failures
  - Frontend builds clean (221 modules)
- Completed Sprint 22 Product UX Polish And Browser QA:
  - Error handling, loading spinners, empty states standardized across 4 first-gen admin CRUD views (Members, Contributions, Events, Announcements)
  - Role-aware routing guard for `/admin/*` routes; `hasRole('admin')` computed helper in auth store
  - UX copy: "Export CSV" / "Cancel" labels aligned across all admin views
  - Mobile offcanvas navigation with hamburger toggle in AppLayout and AdminLayout
  - Role-aware Admin link: hidden from non-admin users in AppLayout sidebar
  - Export CSV logic extracted to `useCsvExport` composable; export buttons disabled during operation with spinner
  - Accessibility: `aria-label` on tables, `scope="col"` on headers, `aria-labelledby` on modals, icon-only button labels, global `:focus-visible` styles
  - Playwright E2E smoke test suite: config + unauthenticated-flow specs (login, admin redirects, health)
  - Backend: 144 tests pass, 0 failures. Frontend: builds clean (222 modules)
  - Playwright E2E smoke tests written (12 tests in 3 spec files) — require running stack to execute
- Completed Sprint 23 Observability And Runtime Reliability:
  - Real `/health` dependency probes for database, Redis, MinIO, Qdrant, and Ollama
  - New `/metrics` endpoint with request, error, ingestion, retry, and chat counters
  - Correlation IDs on responses via `X-Request-ID`
  - Structured error responses with `error_code` and `request_id`
  - Admin ingestion job health summary with queued, processing, failed, completed, and retried visibility
  - Operations documentation for logs, metrics, troubleshooting, and alerting guidance
  - Backend: 149 tests pass, 0 failures

- Completed Sprint 24 Production Validation, Recovery And Security Hardening:
  - Production Docker build validated for API and web
  - Production smoke check passed against `http://localhost`
  - Backup and restore drill passed with a schema wipe and SQL dump restore on PostgreSQL
  - Auth rate limiting hardened for invite, reset-password, and MFA flows
  - Production readiness docs and smoke script added
  - Alembic migration chain repaired and validated from a fresh database

- Completed Sprint 25 Commercial Packaging And Launch Readiness:
  - Commercial packaging docs added for onboarding, admin operations, support, feature matrix, pricing notes, transition checklist, and maturity review
  - README and deployment guide now point to the commercial documentation set
  - Product positioning now explains self-hosted and managed-service offer shapes
  - Foundational roadmap closed; future work should start a new roadmap

- Completed Sprint 26 Public Product Landing And Lead Capture:
  - Public login entry redesigned into a commercial landing surface with value proposition, trust signals, and CTA toward sign-in
  - Existing auth flow preserved while making the public entry page credible for demos and evaluation
  - Browser coverage updated for the public entry surface and login redirects

- Completed Sprint 27 Guided Tenant Onboarding And Conversion Flow:
  - Tenant dashboard now shows a real first-run checklist, progress, next best action, and quick actions
  - Documents and members admin views now expose setup-oriented empty states instead of dead ends
  - Browser validation for login and onboarding now runs autonomously through Playwright with mocked API responses where appropriate
  - Commercial onboarding docs now reflect the in-app guided setup flow

- Completed Sprint 28 Admin Overview And Tenant Operations Hub:
  - `/admin` now exposes real metrics, watchlist items, ingestion health, onboarding continuity, and quick actions instead of placeholder sprint text
  - Module-aware admin widgets now hide correctly when tenant modules are disabled
  - App and admin layouts now react to module-state changes instead of freezing visibility at first render
  - Browser validation covers the authenticated admin hub through autonomous Playwright mocks
- Completed Sprint 29 Team Invitations And Access Operations Console:
  - Admin access console added at `/admin/access` for tenant-scoped invitations and access rollout
- Completed Sprint 45 Treasurer And Auditor Finance Console, including:
  - tenant-wide payment listing and finance report export endpoints with backend capability enforcement
  - enriched treasurer workspace with recent payment activity and stronger day-to-day finance visibility
  - new read-only auditor finance workspace for `auditor`, `president`, `principal_admin`, and `admin`
  - backend authorization tests proving auditors can inspect and export while treasurers cannot access auditor-only export paths
  - browser validation for treasurer finance operations and auditor read-only oversight
  - Tenant role catalog is now exposed through a backend admin-safe endpoint for real role selection in the invite workflow
  - Pending, accepted, cancelled, and expired invitation states are visible in-product with cancellation support
  - Latest invite acceptance URL is surfaced for secure manual sharing while external delivery remains future work
  - Admin overview quick actions now link directly into access operations
  - Frontend admin-route restore behavior was hardened so session restoration does not wrongly eject valid admins
  - Backend invitation and tenant-role tests pass, and autonomous Playwright browser coverage now validates invite creation and cancellation
- Completed Sprint 46 Censor Discipline Workspace, including:
  - dedicated censor workspace route and sidebar/dashboard entry points for censor and authorized executive roles
  - explicit privacy boundaries around disciplinary record browsing and mutation
  - backend audit coverage proving create, update, and delete actions are captured for disciplinary records
  - accessibility improvements for the censor form controls so labels bind correctly to inputs
  - browser validation for censor create/edit/delete flows and role-based denial for treasurer access
- Completed Sprint 47 Sports Operations Workspace, including:
  - dedicated sports workspace route and sidebar/dashboard entry points for sports managers and authorized administrators
  - sports-tagged event management with backend-enforced workspace isolation
  - role-specific write boundaries keeping sports operations separate from generic event administration
  - browser validation for sports create/edit flows and route denial for unrelated roles
- Completed Sprint 48 President And Vice President Governance Cockpit, including:
  - dedicated governance cockpit route and navigation entry points for president and vice president sessions
  - cross-module oversight cards for documents, member directory, announcements, events, finance balance, and audit trail
  - limited executive quick actions that stay subordinate to backend capability enforcement
  - browser validation for president, vice president, and denial paths from unrelated roles
- Completed Sprint 49 Principal Admin Global Control Plane, including:
  - backend tenant-administration surfaces now recognize `principal_admin` as a capability-driven tenant control role
  - notification diagnostics and test dispatch now honor tenant administration capabilities rather than literal `admin`
  - the admin shell and dashboard now present a principal-admin control plane label and quick action path for `principal_admin`
  - browser validation covers the principal-admin dashboard shortcut and admin overview shell labeling
- Completed Sprint 50 Role-Aware Chat And Structured Knowledge Boundaries, including:
  - structured chat context adapters for personal contribution balance and tenant finance summary questions
  - backend refusal guards that block another member's personal finance requests before any LLM call
  - prompt assembly that separates structured context from retrieved document sources
  - chat trace updates that record source types alongside citations and refusal reasons
  - frontend chat and audit views that surface source-type metadata
  - backend chat regression tests proving self-balance, finance-summary, refusal, and traceability behavior
- Completed Sprint 51 Role-Specific Navigation And UX Simplification, including:
  - a shared role-navigation composable that groups member essentials, office workspaces, and admin governance into shorter sections
  - a simplified member shell that foregrounds profile, security, chat, and read-only association links while hiding bureau clutter
  - a simplified admin shell with grouped operations and governance sections
  - a role-aware dashboard that now speaks in member, office, and principal-admin language
  - browser coverage proving the member sidebar stays compact while office and executive pathways remain intact
- Completed Sprint 52 Full Regression Matrix And Professional Release Candidate, including:
  - a release-candidate backend regression matrix covering member, secretary general, treasurer, auditor, censor, sports manager, president, vice president, and principal admin flows
  - a release-candidate browser matrix validating each major role's landing surface and guarded redirects
  - an expanded demo seed with the canonical association role set and corresponding demo credentials
  - an updated demo walkthrough and professional release-candidate checklist for handoff and validation
  - final roadmap, status, and AI handoff updates indicating the current professionalization track is complete
- Completed Sprint 54 Member Renewal, Reminder, And Collections Automation:
  - Added backend reminder history tied directly to contribution records with tenant-scoped reminder logs and audit events
  - Added treasurer-safe reminder dispatch for single contributions and filtered outstanding cohorts through the backend notification-provider layer
  - Added collections reminder controls and recent reminder history to the finance workspace without changing the simple member-facing self-service surface
  - Preserved member privacy boundaries so ordinary members still cannot access tenant-wide reminder or finance history
  - Targeted backend tests, frontend production build validation, and finance browser coverage passed on 2026-07-03
- Completed Sprint 55 Multi-Tenant Provisioning And Demo Operations:
  - Added an operator-safe multi-tenant demo provisioning helper that seeds a second isolated tenant on top of the base demo stack
  - Added a cross-tenant demo user and secondary-tenant admin data so the tenant picker and switcher can be reproduced on a live stack
  - Added browser coverage proving the header tenant switcher updates the active workspace and persists the new tenant selection
  - Updated the README and demo asset documentation so the live multi-tenant walkthrough is reproducible for future agents
  - Validation passed on 2026-07-04: Python helper import check, frontend build, and Playwright tenant-switching coverage
- Completed Sprint 30 Account Security And Identity Self-Service:
  - Authenticated `Account Security` view added at `/account/security` for MFA status, enrollment, verification, disablement, and password recovery launch
  - Backend now exposes a minimal MFA status endpoint without leaking secrets
  - App shell now provides a clear navigation path into account security from sidebar and account menu
  - Invite acceptance, login, forgot-password, and reset-password screens now guide users toward a coherent post-login security posture
  - Logged-in users can trigger the existing password reset flow against their own account from the authenticated shell
  - Autonomous backend and Playwright validation now cover MFA status, enable/disable, and password recovery launch behavior
- Completed Sprint 31 Secure Identity Message Delivery And Access Notifications:
  - Identity invite and forgot-password flows now dispatch through the notification provider abstraction instead of relying only on manual token handoff
  - SMTP-configured email delivery is now supported through the existing email provider, with safe simulated fallback when no provider is configured
  - Invitation responses now expose delivery state (`sent`, `simulated`, `failed`, `manual`) and only reveal raw invite tokens for development, simulation, or failed-delivery fallback
  - Password-reset responses preserve non-enumeration and hide raw reset tokens in production when delivery succeeds through a real provider
  - Admin access UI now surfaces delivery outcome instead of assuming every invite must be manually shared
  - New autonomous backend tests cover sent, simulated, and failed delivery behavior; frontend build and Playwright access-console validation passed
- Completed Sprint 32 Session Governance And Security Event Operations:
  - Persistent user-session inventory now exists in the backend, with `sid`-aware JWT validation and backend-enforced session revocation
  - Authenticated users can now list active sessions, revoke a specific other session, revoke all other sessions, or revoke all sessions from the account-security surface
  - Password reset completion now invalidates all existing sessions, and MFA disablement now revokes other sessions to reduce stale access risk
  - Recent identity security events are now visible from the authenticated security surface and continue to flow through the tenant audit trail
  - Refresh-token validation now depends on the active session record, so revoked sessions cannot mint fresh access tokens
  - Autonomous backend tests, frontend build validation, and Playwright browser coverage passed for the new session-governance workflows
- Completed Sprint 33 Tenant User Lifecycle Governance And Account Lockdown:
  - Backend auth dependency now rechecks active tenant membership on every protected request, so suspended memberships lose effective access immediately
  - Tenant admins can now list managed users, inspect membership status, see active tenant-session counts, and review the latest identity activity from `/admin/access`
  - Admin lifecycle endpoints now support suspension, reactivation, and forced tenant-scoped session revocation for managed users
  - Invitation handling no longer allows suspended or historical memberships to bypass lifecycle controls through a fresh invite
  - Autonomous backend tests, frontend build validation, and Playwright browser coverage passed for managed-user lifecycle operations
- Completed Sprint 34 Authentication Hardening And Recovery Stability:
  - Backend refresh-token validation now fails safely when the active session's tenant membership has been suspended or invalidated
  - MFA completion now preserves the multi-tenant organization-picker flow instead of dropping multi-membership users directly into the app
  - Login, invitation acceptance, forgot-password, reset-password, and MFA views now surface clearer backend-aligned recovery and denial messages
  - New autonomous browser coverage validates suspended-access denial, MFA multi-tenant continuation, expired invitation feedback, used reset-link feedback, and redirect preservation
  - Targeted backend tests, frontend production build validation, and Playwright authentication regression coverage passed for the sprint
- Completed Sprint 43 Member Self-Service And Personal PDF Statements:
  - Added authenticated member-only statement endpoints for personal contribution history, consolidated statement data, and PDF download
  - Added backend PDF generation for personal contribution statements without exposing another member selector or cross-member export path
  - Hardened integration tests to prove a member sees only personal statement data and personal PDF content
  - Reworked the member self-service view into a cleaner workspace focused on profile, balance, contribution history, and statement download
  - Targeted backend tests passed and the frontend production build passed
- Completed Sprint 72 Role Journey Polish, Workspace Clarity, And Recovery-Oriented UX:
  - Added a shared `useRecoveryState` composable centralizing loading, error, and retry behavior for role workspaces
  - Member self-service and treasurer finance workspaces now present a coherent recovery alert with a localized retry control and a privacy-safe recovery hint
  - Added `common.retry` and `common.recoveryHint` i18n keys across FR/EN/DE plus `finance.workspaceErrorTitle`
  - Frontend type-check, production build, and a new autonomous Playwright recovery test all pass
  - Backend suite (239 tests) remains green; changes are frontend-only and preserve tenant isolation and backend-enforced permissions
- Completed Sprint 73 Open-Source Release Readiness, Publication Pack, And Post-Track Handoff:
  - Created `docs/OPEN_SOURCE_RELEASE.md` with a verified baseline, open-source release checklist, explicit known limits, non-regression boundaries, and next-planning-cycle themes
  - Extended `CONTRIBUTING.md` with issue/PR reporting, private security disclosure, and a pointer to known limits
  - Refreshed `RELEASE_NOTES.md` with the verified test/type-check/build/E2E baseline, the role model and boundaries, and honest limitations
  - Corrected the backend test count in `README.md` (239 integration tests, SQLite)
  - Verified the documented baseline: 239 backend tests pass, `npm run type-check` and `npm run build` pass, localization E2E (7 tests) passes
  - Closed the stabilization and open-source maturity track; future work starts a new planning cycle
- Completed Sprint 74 Broader Recovery UX Rollout (Censor + Sports):
  - Migrated `CensorWorkspaceView.vue` and `SportsWorkspaceView.vue` to the shared `useRecoveryState` composable
  - Replaced bespoke inline error blocks with the standardized recovery alert (title + message + recovery hint + retry button with spinner)
  - Added `censor.workspaceErrorTitle` and `sports.workspaceErrorTitle` i18n keys across FR/EN/DE
  - Added E2E recovery tests for censor (fr) and sports (de) retry-after-failure flows
  - Verified: 239 backend tests pass, frontend type-check and build pass, localization E2E (9 tests) passes; changes are frontend-only and preserve tenant isolation and backend-enforced permissions
- Completed Sprint 89 Quality Gate Expansion And CI Hardening:
  - Applied safe ruff autofixes across critical backend modules (core/, chat/, tenancy/, identity/, documents/, membership/, contributions/, events/, disciplinary/, audit/, rag/, tests/)
  - Expanded ruff CI baseline from 6 individual files to 12 directory/module paths with `--ignore E501` for cosmetic line-length tolerance
  - Expanded mypy CI baseline from 4 files to 9 files (added capabilities.py, rag/policy.py, rag/confidence.py, rag/ranking.py, rag/retrieval.py, chat/domain_policy.py)
  - Fixed 2 B904 (raise ... from None) and 1 UP007 (Union → `|`) issues in identity module
  - Updated validation-baseline.md, CI config, and README test count to 264
  - Verified: ruff expanded set passes, mypy expanded set stable (no new pre-existing errors), 264 backend tests pass, frontend type-check and build pass, 19/20 E2E pass (1 pre-existing notification test failure unrelated to this sprint)
- Completed Sprint 90 Full Backend Quality Gate Expansion And Seed Bug Fix:
  - Expanded ruff CI baseline from 12 module paths to cover ALL `app/` modules and all tests
  - Fixed genuine bug in `seed_multi_tenant.py`: `demo_membership` referenced before assignment (was `switcher_membership`, created but never captured)
  - Fixed 8 remaining ruff issues: 2 unused imports in providers/llm/__init__.py (added `__all__`), 1 B904 in worker/tasks/ingestion.py (added `from exc` chain), 5 S314 in providers/parsers/xlsx_xml.py (added per-file ignore for internal auth-gated parser)
  - Added `defusedxml`-equivalent S314 suppression for the internal xlsx/xml parser via per-file-ignore in pyproject.toml
  - Updated validation-baseline.md and CI config to reflect the full `app/` ruff baseline
- Completed Sprint 91 Pre-Existing Mypy Error Resolution And Baseline Expansion:
  - Fixed `CurrentUser.user` type in dependencies.py: changed from `object` to `"User"` using TYPE_CHECKING pattern (resolved 5 `"object" has no attribute "id"` errors across tenancy/router.py)
  - Fixed tenancy/repository.py SQLAlchemy type issues (4 errors: `# type: ignore[assignment]` for JSON columns and PostgreSQL dialect, `# type: ignore[arg-type]` for list() call)
  - Fixed tenancy/service.py: added type annotations for `branding_raw` and `settings_raw` (2 errors)
  - Fixed notifications/placeholders.py: added `assert settings.smtp_host is not None` guard (2 errors)
  - Fixed qdrant.py: corrected union narrowing for `VectorParams` and added `# type: ignore[union-attr]` for query results (5 errors)
  - Fixed LLM provider protocol in base.py: removed `async` from `generate_stream` signature to match async generator implementations (2 errors)
  - Expanded mypy CI baseline from 4 individual files to 7 directory/module paths: `core/`, `chat/domain_policy.py`, `rag/`, `tenancy/`, `providers/llm/base.py`, `providers/notifications/`, `providers/vector_store/`
  - Updated validation-baseline.md and CI config to reflect the expanded mypy baseline
  - Verified: mypy passes on all 24 checked source files with zero errors; 264 backend tests pass; frontend type-check and build pass
- Completed Sprint 44 Secretary General Workspace And Document Governance:
  - Added a dedicated secretary workspace with role-scoped navigation and a focused overview surface
  - Reused the existing document, policy, and announcement management flows through secretary-only routes instead of forcing office staff into the admin console
  - Hardened frontend route protection so direct navigation to guarded workspaces restores session state before evaluating role access
  - Added backend coverage proving the secretary general can manage documents, policies, and announcements but cannot mutate finance or disciplinary records
  - Added browser validation for secretary workspace navigation and finance-route denial, and made Playwright port selection configurable for reproducible local runs
- Completed Sprint 35 Operational Reliability, Data Safety, And Migration Discipline:
  - Created `scripts/restore.sh` to automate full restoration of PostgreSQL, Redis, Qdrant, MinIO, and Ollama from backup archives
  - Added Docker healthchecks for api, worker, and web services in docker-compose.yml
  - Created migration `0009_user_sessions` for the missing `user_sessions` table (Sprint 32 model was never migrated)
  - Created migration `0010_document_version_fk` for the missing FK constraint on `documents.current_version_id`
  - Fixed `contributions/models.py` numeric column annotations to match migration precision
  - Updated `scripts/production_smoke.sh` with response body validation and detailed pass/fail reporting
  - Added 8 health endpoint tests covering response shape, per-service status, and Prometheus metrics
  - Fixed pre-existing `test_audit_trail_is_tenant_scoped` failure caused by login audit event logging
  - Updated deployment guide with automated restore procedure
  - Backend: 171 tests pass, 0 failures

- Completed Sprint 36 Association Operations Robustness:
  - Phase 1 — Backend schema enum validation and cross-field validators for all 6 association modules:
    - Membership: `EmailStr` on email field, `MembershipStatus` enum, `min_length`/`max_length` constraints on name/code fields
    - Contributions: `ContributionStatus`/`PaymentMethod` enum, `currency` Literal with `max_length=3`, numeric `ge=0` constraints
    - Events: `EventStatus`/`EventVisibility` enum, `@model_validator` enforcing `end_at` after `start_at`
    - Announcements: `AnnouncementVisibility` enum, `@model_validator` enforcing `expires_at` after `published_at`, `body` `max_length=50000`
    - Policies: `PolicyStatus` enum, `description` `max_length=10000`
    - Disciplinary: `DisciplinaryStatus` enum, `currency` Literal with `max_length=3`
  - Phase 2 — Backend tests for previously untested endpoints (10 new tests):
    - Contributions: PATCH, DELETE, by-member list, payment list
    - Policies: GET by ID, admin list all, PATCH, DELETE
    - Disciplinary: PATCH, DELETE
  - Phase 3 — Frontend improvements:
    - Created reusable `ConfirmModal.vue` component (Bootstrap 5 modal) with delete/cancel actions
    - Replaced raw `confirm()` dialogs in Events, Announcements, Policies, Disciplinary, and Contributions admin views
    - Added try/catch error handling on all delete operations (Events, Announcements)
    - Replaced raw UUID text input in Contributions create form with member dropdown selector
  - Backend: 181 tests pass, 0 failures
  - Frontend: builds clean (234 modules)

- Completed Sprint 37 Final Open-Source Release Stabilization And Portfolio Readiness:
  - Centralized API version in `app/_version.py`, removed 3 hardcoded copies in `main.py`
  - Fixed `health_checks.py:run_all_checks()` return type annotation (`-> list[dict]` → `-> dict[str, dict]`)
  - Added proper return type annotations to all 5 provider factory functions in `dependencies.py`
  - Removed stale files (`test_debug.py`, `UNKNOWN.egg-info/`)
  - Created `seed/sample-members.csv` and `seed/sample-contributions.csv` with reference in import-export docs
  - Created `CONTRIBUTING.md` with development workflow and conventions
  - Created `RELEASE_NOTES.md` (v0.1.0) with overview, architecture, test coverage, and known limitations
  - Updated `README.md` test count from "82+" to "181+"
  - Updated `docs/ai/NEXT_SPRINT.md` and `docs/ai/PROJECT_STATE.md` for final release state
  - Updated `IMPLEMENTATION_ROADMAP.md` — Sprint 37 marked completed
  - Backend: 181 tests pass, 0 failures
  - Frontend: builds clean (234 modules)
- Completed Sprint 38 Treasurer Workspace And Finance Permission Hardening:
  - Backend membership and contributions routers now enforce explicit role gates instead of relying on comments or implicit assumptions
  - Membership endpoints now split correctly between `admin`-only mutation/export/import and `admin`/`treasurer` finance lookup operations
  - Contribution endpoints now split correctly between `admin`-only delete/export/import and `admin`/`treasurer` finance operations
  - Added same-tenant integration-test helper `create_user_for_tenant()` for realistic role scenarios
  - Added backend regression tests proving plain members receive `403` on staff finance endpoints and treasurers can work without admin-only export/delete rights
  - Added authenticated frontend route `/finance` with a dedicated treasurer workspace
  - Added member balance lookup, contribution creation, payment recording, and year-scoped finance summary in the new workspace
  - Fixed the AppLayout role-visibility bug that rendered the Admin link for non-admin users because a computed ref returned by `hasRole()` was used directly in the template
  - Added Playwright browser coverage for the treasurer finance workspace with mocked API flows
  - Backend targeted suite: 17 tests passed
  - Frontend build passed
  - Playwright finance workspace suite: 2 tests passed
- Completed Sprint 39 Role-Aware Dashboard And Action Surface Hardening:
  - Dashboard quick actions now adapt to the authenticated role instead of always advertising admin-only routes
  - Treasurers now see finance-first shortcuts plus role-appropriate review links instead of tenant-settings and member-import CTAs
  - Tenant onboarding checklist now includes a finance workspace step for admin/treasurer sessions and marks admin-only setup items explicitly
  - Role-aware dashboard browser coverage now validates the treasurer quick-action surface
  - Frontend type-check passed
  - Frontend build passed
  - Playwright dashboard treasurer test passed
- Completed Sprint 40 Demo Gallery And Handoff Polish:
  - Regenerated the GitHub demo screenshot gallery from the current codebase
  - Updated the treasurer session to showcase the dashboard, finance workspace, and account security flows
  - Added a finance-workspace screenshot to the README gallery
  - Refreshed the reusable continuation prompt for Codex, Cursor, and GitHub Copilot
  - Restored the demo/gallery docs to match the verified runtime surface
- Completed Sprint 41 Governance Role Matrix And Capability Foundation:
  - Added a canonical association role catalog covering `principal_admin`, `president`, `vice_president`, `secretary_general`, `treasurer`, `auditor`, `censor`, `sports_manager`, and `member`
  - Added a reusable backend capability matrix plus legacy `admin` compatibility for the transition track
  - Extended `CurrentUser` with capability checks for backend authorization composition
  - Tenant role listing now auto-syncs the canonical catalog and returns capability metadata
  - Added a tenant-scoped managed-user role replacement endpoint with audit logging for role changes
  - Invitation acceptance now records explicit audited role-assignment events for canonical roles
  - Seed data now provisions the canonical governance role catalog alongside the legacy compatibility roles
  - Added targeted governance tests and passed targeted validation for Sprint 41
- Completed Sprint 42 Fine-Grained Backend Permission Enforcement:
  - Added a shared backend capability enforcement helper under `app/core/authorization.py`
  - Migrated membership, contributions, documents, policies, disciplinary, events, announcements, audit, and admin operational routers away from broad inline `admin` / `admin,treasurer` checks
  - Mapped backend actions to explicit capabilities such as membership read/write, finance read/write, document governance write, policy write, disciplinary read/write, event write, announcement write, audit read, and tenant administration
  - Kept legacy `admin` compatibility while enabling canonical roles such as `secretary_general`, `auditor`, `censor`, `sports_manager`, and `principal_admin`
  - Updated policy and disciplinary service interfaces to consume capability-driven access semantics instead of hardcoded admin/staff booleans
  - Added targeted integration tests for secretary general, sports manager, auditor, censor, principal admin, and denial paths for over-broad roles
  - Passed targeted backend validation suites for authorization-sensitive modules and governance continuity

## Current Verified Product Surface

- Vue frontend with login (multi-tenant flow), guided onboarding dashboard with role-aware quick actions, app shell (with real tenant switcher and branding), authenticated account security view, dedicated finance workspace for `treasurer` and `admin` users, admin shell (with brand-aware UI), real admin overview hub, admin access and lifecycle console, admin documents view, admin chat audit view, member profile view, admin members view (with CSV import/export), admin contributions view (with CSV import/export), public policies view, member disciplinary view, admin policies view, admin disciplinary view, member events view, admin events view (with CSV export), member announcements view, admin announcements view (with CSV export), admin notification extensions view, admin tenant settings view, and a refreshed GitHub demo gallery plus universal handoff prompt pack.
- FastAPI backend with mounted `auth`, `tenants`, `documents`, `admin`, `chat`, `membership`, `contributions`, `events`, `announcements`, and `notifications` routers plus `/health` and `/metrics`. Identity routes now include invitation lifecycle, password reset, MFA status, enrollment, verification, disablement, managed-user lifecycle controls, and tenant-scoped session containment.
- PostgreSQL-backed identity, tenancy, document, version, ingestion-job, chunk, membership, contribution, payment, event, and announcement models.
- MinIO-backed object storage provider.
- Redis and Celery ingestion worker flow.
- Parsers for TXT, Markdown, CSV, PDF, DOCX, WhatsApp exports, and OCR for image documents.
- Ollama embedding provider and Qdrant indexing provider.
- First RAG chat surface with permission-aware retrieval, structured authorization boundaries, no-source refusal, citations, and LLM provider abstraction.
- Admin document access controls, admin reindex endpoint, and admin chat query traceability endpoint.
- Membership profiles with CRUD, tenant isolation, and self-view.
- Contribution records with balance calculation and payment recording.
- Public policy browsing and admin policy management.
- Private disciplinary records with role-based staff management.
- Events and announcements with visibility scoping and admin CRUD.
- Optional multi-channel notification foundation with a real SMTP-backed email path plus simulated Telegram and WhatsApp providers.
- Hardened AI safety: prompt injection defenses in system prompt, untrusted source demarcation,
  access control enforcement before prompt assembly, no-source refusal behavior, citation verification
- Enhanced admin audit view with search, status filter, and summary statistics
- Tenant audit trail API with CSV export and admin filtering for sensitive actions
- Production deployment infrastructure:
  - nginx.conf for production frontend serving with SPA fallback and API proxy
  - docker-compose.prod.yml override for production builds
  - .env.production.example with hardened defaults
  - Cloudflare Tunnel config with security documentation
  - Caddy reverse proxy config with TLS and security headers
  - Automated backup script for all persistent volumes
  - Comprehensive deployment guide (docs/deployment-guide.md)
- Fully autonomous backend test suite using SQLite by default, without requiring a local PostgreSQL instance.
- Demo walkthrough documentation covering all roles (admin, member, treasurer), AI safety, and tenant isolation.
- Tenant settings API with module toggle controls (8 modules configurable per tenant).
- Admin settings view in Vue frontend for branding and module configuration.
- Multi-tenant auth: API-driven membership loading, tenant switching with JWT re-issuance, and post-login tenant picker.
- MIT License file.
- Enhanced `/health` endpoint returning available module list and real dependency probes for database, Redis, MinIO, Qdrant, and Ollama with per-service status and latency.
- `/metrics` endpoint and admin ingestion job health summary for runtime visibility.
- Module toggles enforced at backend router level: disabled modules return 403 with module name in detail.
- Frontend route guard redirects disabled module routes to dashboard.
- Admin data-warning before disabling modules that have existing business records.
- Admin access console for invitations with tenant role selection, pending/cancelled visibility, and secure acceptance-link handoff.
- Authenticated account security surface for MFA status, self-service MFA management, and password recovery launch.
- Identity message delivery pipeline for invitations and password recovery with SMTP-backed email support, delivery-state visibility, and safe token fallback rules.
- Persistent session governance with active-session inventory, targeted revocation controls, revoke-all flows, and recent security-event visibility for authenticated users.
- Tenant user lifecycle governance with backend-enforced suspension, reactivation, admin-visible identity state, and tenant-scoped forced session revocation.
- Canonical governance role catalog and backend capability foundation for the professional association track, including audited managed-user role changes.

## Known Risks

- The backend capability layer is now wired into the major association modules, and the main dashboard/workspace entry surfaces now reflect it more faithfully, but the chatbot authorization surface still needs the same rigor role by role.
- The current chatbot is now stronger on structured member-finance boundaries, but broader role-aware coverage for other approved domains still needs work.
- Dedicated workspaces for secretary general, auditor, censor, sports manager, president, vice president, and principal administrator are still roadmap work, not completed product surface.
- `allowed_role_ids` naming still reflects the upload/API contract and should be revisited if we want UUID-backed role targeting later.
- The login and dashboard Playwright coverage now runs autonomously, but broader end-to-end admin/business flows still need a live API stack. See `apps/web/e2e/`.
- Health endpoint probes Redis, MinIO, Qdrant, and Ollama with per-service status/latency.
- Dashboard sprint roadmap may display stale data if not updated as sprints progress.
- Production Docker builds (web production target) have not been tested end-to-end with Docker; the nginx.conf is syntactically correct but needs a real Docker build to confirm.
- Cloudflare Tunnel setup instructions are documented but not yet validated with a real tunnel integration test.
- Backup script is a bash script and may need adaptation for non-Linux hosts (Docker Desktop on Windows/macOS paths).
- Telegram and WhatsApp remain placeholders only; no real external gateway integration has been validated yet beyond the SMTP-backed email path.
- A deeper first-run wizard is still a future enhancement beyond the current guided checklist and action-oriented empty states.
- Only the email channel is wired for real identity delivery and live operator dispatch today; Telegram and WhatsApp remain simulated extension placeholders.
- Identity emails currently use a plain-text branded baseline template and do not yet provide rich HTML theming or provider-side webhook reconciliation.
- The original open-source stabilization target ended at Sprint 37; the product is now entering a second track focused on professional association role coverage and maturity.
- The new execution path is explicit: Sprint 65 was the final planned productization sprint in the current roadmap.
- Sprint 26 has been completed with the public entry commercial surface.
- Sprint 27 has been completed with guided onboarding for new tenant admins.
- Sprint 28 has been completed with a real admin operations hub.
- Sprint 29 has been completed with in-product invitation management.
- Sprint 30 has been completed with self-service account security UX.
- Sprint 31 has been completed with secure outbound identity delivery and delivery-state visibility.
- Sprint 32 has been completed with session governance and current-user security event operations.
- Sprint 33 has been completed with tenant user lifecycle governance and account lockdown.
- Sprint 34 has been completed with authentication hardening and recovery stability.
- Sprint 35 has been completed with operational reliability, migration gap fixes, restore automation, and Docker healthchecks.
- Sprint 38 has been completed with treasurer workspace activation and finance permission hardening.
- Sprint 39 has been completed with role-aware dashboard and action-surface hardening.
- Sprint 40 has been completed with demo gallery and handoff polish.
- Sprint 64 has been completed with scripted deployment packaging, upgrade, rollback, and smoke-validation automation.
- Sprint 65 has been completed with the commercial offer pack, support-boundary clarification, buyer FAQ, and final market-facing documentation sync.
- Sprint 58 has been completed with the tenant operations command center, explicit membership inventory, and confirmation-based tenant switching.
- Sprint 66 has been completed with access-policy parity, RAG safety hardening, and locale contract enforcement.
- Sprint 67 has been completed with French-first translation completion across all primary admin, finance, and workspace views, plus i18n governance rules.
- The current stabilization roadmap remains active, with Sprint 68 through Sprint 73 still planned for execution.

## Next Session Rule

Future agent sessions must not continue from memory alone.

They must read:

1. `constitution/KAIRO_CONSTITUTION.md`
2. `IMPLEMENTATION_ROADMAP.md`
3. `PROJECT_STATUS.md`
4. `prompts/CODEX_AUTOPILOT.md`
5. `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

Then they must determine the current sprint and continue only that sprint or the next unfinished sprint.
