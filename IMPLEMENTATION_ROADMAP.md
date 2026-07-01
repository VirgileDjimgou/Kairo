# Implementation Roadmap

This roadmap is the executable sprint plan for Kairo. Each sprint must be completed independently and the status files must be updated before the next sprint starts.

## Completion Rules

A sprint is complete only when:

- relevant build checks pass
- relevant tests pass
- documentation is updated
- architecture boundaries are preserved
- tenant isolation is preserved
- unresolved critical risks are explicitly listed
- `PROJECT_STATUS.md` reflects the new state

## Sprint 0 - Foundation And Repository Skeleton

Status: Completed

Goal:
Establish the repository as a durable monorepo that any agentic IDE can resume safely.

## Sprint 1 - Identity, Tenancy And Auth

Status: Completed

Goal:
Implement the minimal security foundation with JWT auth, tenant membership, and role resolution.

## Sprint 2 - Professional Vue Layout

Status: Completed

Goal:
Build the first portfolio-grade user shell with login, dashboard, app layout, and admin layout.

## Sprint 3 - Document Upload And Object Storage

Status: Completed

Goal:
Allow authenticated tenant users to upload documents and persist document metadata plus stored originals.

## Sprint 4 - Ingestion Worker And Parsing

Status: Completed

Goal:
Extract text from supported uploaded documents and persist chunk-ready ingestion results.

## Sprint 5 - Embeddings And Qdrant Indexing

Status: Completed

Goal:
Embed document chunks and store tenant-scoped vector payloads in Qdrant.

## Sprint 6 - First RAG Chat

Status: Completed

Goal:
Implement the first secure retrieval and answer flow with citations.

Deliverables:

- `rag` module
- `chat` module
- first LLM provider abstraction
- Ollama generation provider
- permission-aware retrieval filter builder
- first chat query endpoint
- no-source refusal behavior
- tests for tenant and access-scope retrieval safety

## Sprint 7 - Admin RAG Controls

Status: Completed

Goal:
Give administrators operational control over document access, ingestion, and answer traceability.

## Sprint 8 - Membership And Contributions

Status: Completed

Goal:
Add structured member and contribution records with self-view and privileged back-office views.

Deliverables:

- MembershipProfile, ContributionRecord, PaymentRecord ORM models
- Full CRUD API for member profiles (admin)
- Full CRUD API for contribution records (admin/treasurer)
- Payment recording with automatic balance recalculation
- Contribution summary endpoint (aggregate expected/paid/balance)
- Member self-view endpoints (profile + balance)
- Tenant isolation enforced on every membership and contribution query
- Admin members management view (list, create, edit, delete)
- Admin contributions management view (list, create, record payments)
- Member profile self-view (profile card + balance summary)
- Backend integration tests (11 tests, all passing)
- Frontend build passing

Acceptance criteria:

- member sees only personal profile and balance
- admin can create/edit/delete member profiles
- admin can create contributions and record payments
- balance auto-calculates from expected minus paid
- tenant A members are invisible to tenant B

## Sprint 9 - Policies, Rules And Discipline

Status: Completed

Goal:
Support association/business policies and procedures.

Deliverables:

- PolicyRecord model
- DisciplinaryRecord model
- rule category management
- private disciplinary records
- role-based access rules

Acceptance criteria:

- user can ask about public policies
- user cannot see another user's disciplinary record
- admins can manage policy documents

## Sprint 10 - Events And Announcements

Status: Completed

Goal:
Add calendar and announcement capabilities for tenant operations.

Deliverables:

- Event ORM model with visibility_scope, status, start_at/end_at, and location
- Announcement ORM model with visibility_scope, published_at, and expires_at
- Full CRUD REST API for events (admin) and public listing endpoint (members)
- Full CRUD REST API for announcements (admin) and active listing endpoint (members)
- Visibility scope filtering (admin_only hidden from non-admin users)
- Active announcement filtering by publish/expiry dates
- Admin-only enforcement on create, update, delete
- Tenant isolation on all event and announcement queries
- Frontend member views: EventsView (upcoming events) and AnnouncementsView (active announcements)
- Frontend admin management views: AdminEventsView and AdminAnnouncementsView with CRUD modals
- Frontend Vue Router routes for member and admin event/announcement pages
- Sidebar navigation links in AppLayout and AdminLayout
- Backend integration tests: 13 tests covering CRUD, visibility scoping, admin enforcement, tenant isolation, and date-based filtering

Acceptance criteria:

- admin can create, list, update, and delete events
- admin can create, list, update, and delete announcements
- member sees only published, non-admin_only events and announcements
- expired announcements are excluded from the active endpoint
- tenant A events/announcements are invisible to tenant B
- non-admin users cannot create, update, or delete events or announcements

## Sprint 11 - Cloudflare Tunnel Deployment

Status: Completed

Goal:
Document and harden local-first remote exposure for demo and small production-like setups.

Deliverables:

- cloudflared config sample with setup instructions and security notes
- Deployment guide covering architecture, prerequisites, environment config, reverse proxy, Cloudflare Tunnel, backup/restore, and security checklist
- Caddy reverse proxy config sample (Caddyfile) with SPA fallback, API proxy, TLS, and security headers
- Caddy docker-compose include file for easy deployment alongside the stack
- Production nginx.conf for frontend Dockerfile (was missing, unblocking production frontend builds)
- docker-compose.prod.yml override switching web and api to production targets
- .env.production.example with hardened defaults and all required variables documented
- Backup script (scripts/backup.sh) for all persistent Docker volumes
- CORS documentation and hardening notes in environment files
- Updated Project Status and Implementation Roadmap

Acceptance criteria:

- user can expose local app through Cloudflare Tunnel
- docs explain setup clearly
- no secrets are committed
- frontend Docker production build can succeed (nginx.conf exists)
- production docker compose override switches to optimized builds
- backup script captures all persistent data
- security checklist is documented and actionable

## Sprint 12 - Evaluation And AI Safety

Status: Completed

Goal:
Add prompt-injection tests, no-source answer rules, and retrieval safety verification.

Deliverables:

- Hardened system prompt with explicit untrusted source boundary and anti-injection rules
- Source demarcation using <sources> tags in the user prompt
- Prompt injection tests (5 tests): system prompt guards, source tag wrapping, access control
  enforcement for injection documents, no-source refusal after hardening, admin-only document
  protection against injection content
- Retrieval evaluation tests (4 tests): citation presence, excerpt correctness, top_k limiting,
  confidence scoring
- Enhanced admin audit review screen: search by question text, status filter (all/answered/refused),
  configurable result limit, summary statistics cards

## Sprint 13 - Demo Tenant And Portfolio Polish

Status: Completed

Goal:
Prepare a recruiter-friendly and client-friendly local demo.

Deliverables:

- Enhanced seed script (`services/api/app/db/seed.py`) with comprehensive demo tenant data
  - Tenant: "Acme Community Organization" (slug: demo, anonymized, not COMBIS)
  - Users: admin, 2 members, treasurer
  - Roles: admin, member, treasurer with granular permission assignments
  - Membership profiles with sample data
  - Sample documents with versions and chunks (bylaws, meeting minutes)
  - Sample policies (fee policy, attendance policy, code of conduct)
  - Sample contributions and payments with balance calculations
  - Sample disciplinary record linked to policy
  - Sample events (upcoming and past) with visibility scoping
  - Sample announcements (active, expired, tenant_public)
- Updated README.md with ASCII architecture diagram, enhanced quickstart, demo credentials table, project structure, and links to deployment guide
- Demo walkthrough script (`docs/demo-script.md`) covering admin, member, treasurer, AI safety, and tenant isolation
- Convenience seed helpers in `seed/` directory (PowerShell and bash)
- All 82 backend tests pass, 0 failures
- Updated PROJECT_STATUS.md and IMPLEMENTATION_ROADMAP.md

Acceptance criteria:

- recruiter can run docker compose up, seed, and explore the full app in under 5 minutes
- demo data is plausible but not tied to any real organization
- README is clear enough for a non-technical evaluation
- existing tests are not broken

## Sprint 14 - Multi-Channel Extensions

Status: Completed

Goal:
Add optional messaging and notification provider extensions without polluting the core product.

Deliverables:

- Notification provider abstraction isolated under `providers/notifications`
- Optional placeholder providers for Email, Telegram, and WhatsApp
- Admin-only diagnostics endpoint listing available channels and configuration state
- Admin-only simulated dispatch endpoint for multi-channel notification tests
- Vue admin notification console for channel status and dry-run dispatch
- Integration tests covering provider discovery, admin-only enforcement, and simulated dispatch

Acceptance criteria:

- web remains the primary user channel
- optional providers do not pollute core document/chat/business modules
- non-admin users cannot access notification extension endpoints
- admins can inspect available channels and run simulated notification tests without external dependencies

## Sprint 15 - Commercialization Baseline

Status: Completed

Goal:
Prepare onboarding, settings, observability, backup posture, and product readiness foundations.

Deliverables:

- Tenant settings API (`GET/PUT /api/v1/tenants/{id}/settings`) with full CRUD support
- Module toggle utility (`modules/tenancy/module_toggles.py`) with 8 known modules and default-enabled configuration
- Pydantic schemas for `TenantSettingsResponse`, `TenantSettingsUpdate`, `BrandingConfig`, `ModuleToggles`
- Repository method `update_tenant()` for in-place tenant field updates
- Admin-only enforcement on settings update endpoint
- Frontend `AdminSettingsView.vue` with organization info, branding (color picker + logo URL), and module toggle checkboxes
- Admin sidebar "Settings" link with gear icon
- Route `/admin/settings` added to Vue Router
- Enhanced `/health` endpoint returning available module list
- MIT `LICENSE` file added
- Updated seed.py demo tenant with default module toggles enabled
- 86 backend tests pass, 0 failures
- Frontend builds clean (206 modules)
- Updated PROJECT_STATUS.md and IMPLEMENTATION_ROADMAP.md

## Sprint 16 - Tenant Activation And Multi-Tenant UX

Status: Completed

Goal:
Turn multi-tenancy from a backend capability into a coherent end-user experience with first-tenant activation, real tenant selection, and branded runtime behavior.

Why this sprint now:

- Sprint 15 introduced tenant settings and module toggles, but the user-facing tenant experience is still partial.
- Commercially, the platform cannot scale to multiple customer organizations if tenant selection stays placeholder-driven.
- This sprint unlocks the next layers of product hardening by making tenant context explicit everywhere.

Primary dependencies:

- Existing auth, tenancy, and settings APIs from Sprints 1 and 15
- Existing frontend auth store and shell layouts
- Seed/demo tenant data from Sprint 13

Execution scope:

- Backend tenant membership discovery and selection flow
- Frontend authenticated tenant bootstrap
- First-run tenant activation UX
- Tenant-aware branding and module-aware navigation
- Regression-safe test coverage for multi-tenant switching behavior

Deliverables:

- Tenant-aware login flow in the frontend with explicit organization selection or tenant slug input
- Real tenant list loading from API instead of placeholder tenant data in the frontend store
- Post-login tenant switcher backed by authenticated tenant membership data
- First-use activation path for a newly created tenant admin
- Frontend branding application from tenant settings (name, colors, logo) across layouts
- Module-aware navigation hiding disabled modules in the sidebar and dashboard
- Graceful empty states when a tenant has no documents, no members, or no enabled modules yet
- Backend support for tenant membership listing optimized for the frontend switcher flow
- Tests for login/tenant selection behavior and module-aware navigation rendering
- Documentation update describing the real multi-tenant UX model

Detailed implementation slices:

- Auth and tenancy API
  - add or refine endpoint(s) that return the current user tenant memberships with tenant metadata, role summary, branding summary, and enabled modules
  - ensure the post-login payload gives the frontend enough information to bootstrap the active tenant without hardcoded defaults
  - define safe behavior when a user has zero memberships, exactly one membership, or multiple memberships
- Frontend auth bootstrap
  - replace placeholder tenant arrays in stores with API-backed membership loading
  - persist the active tenant choice safely across refreshes without trusting stale client-only state
  - handle invalid remembered tenant selections gracefully
- Tenant activation experience
  - provide a clean first-use state for newly created tenant admins
  - define the minimum information needed to activate or personalize a tenant after first login
  - make sure this path works even if there is no content yet
- Product shell adaptation
  - apply tenant branding consistently in layout header, sidebar, dashboard, and high-visibility UI accents
  - hide disabled modules from dashboard cards, primary navigation, and quick actions
  - display useful empty states instead of broken or blank screens
- Safety and consistency
  - ensure tenant switching clears or refreshes any stale tenant-scoped cached data
  - verify that switching tenants never exposes data from the previous tenant in the UI
  - verify that frontend tenant switching remains subordinate to backend authorization

Validation requirements:

- backend integration tests for membership listing and tenant bootstrap response shape
- frontend tests for tenant selection, remembered tenant restoration, and disabled-module navigation filtering
- manual browser validation for login -> tenant selection -> dashboard -> tenant switch -> logout

Definition of done:

- all tenant choices shown in the frontend come from the real API
- tenant switch changes the effective product shell without page corruption or stale data leakage
- branded shell and module-aware navigation behave consistently after refresh
- status docs point to Sprint 17 as next only after Sprint 16 is fully completed

Acceptance criteria:

- a user with multiple tenant memberships can explicitly choose the target tenant
- the sidebar and dashboard reflect the currently selected tenant
- tenant branding is visible in the product shell after login
- disabled modules are not shown in navigation for that tenant
- the frontend no longer relies on hardcoded placeholder tenant options

Deliverables:

- Backend: `GET /api/v1/auth/me` now returns `memberships` array with tenant metadata, branding, module toggles, and roles
- Backend: `POST /api/v1/auth/switch-tenant` endpoint issues a new JWT scoped to the target tenant
- Backend: Membership resolution with branding/module parsing in `AuthService.get_user_memberships()`
- Frontend: `tenant.store.ts` rewritten — hardcoded placeholder tenants replaced with API-driven membership loading
- Frontend: `auth.store.ts` updated to sync memberships to tenant store on login/session restore
- Frontend: `LoginView.vue` now shows tenant picker after login when user has multiple memberships
- Frontend: `AppLayout.vue` applies tenant branding (primary color), filters sidebar by enabled modules, and uses real API-backed tenant switcher
- Frontend: `AdminLayout.vue` filters sidebar navigation by enabled modules per tenant settings
- Frontend API client extended with `TenantMembershipResponse`, `SwitchTenantRequest/Response` types
- 5 new backend integration tests for switch-tenant and /me memberships
- 91 total backend tests pass, 0 failures
- Frontend builds clean (206 modules)
- Updated PROJECT_STATUS.md, IMPLEMENTATION_ROADMAP.md, NEXT_SPRINT.md, and PROJECT_STATE.md

## Sprint 17 - Identity Lifecycle And Access Hardening

Status: Completed

Goal:
Make account access management commercially credible with invitation flows, password lifecycle tooling, and stronger authentication posture.

Why this sprint now:

- Once tenant activation is real, onboarding and account recovery become immediate commercial blockers.
- A product positioned for real customers needs lifecycle management beyond seed users and manual database setup.
- This sprint reduces operational fragility before broader adoption.

Primary dependencies:

- Stable tenant membership flow from Sprint 16
- Existing auth module and role assignment foundations from Sprint 1

Execution scope:

- invitation and onboarding lifecycle
- password reset and recovery lifecycle
- admin-oriented authentication hardening
- token expiry, abuse resistance, and auth edge-case coverage

Deliverables:

- Invitation model and token flow for inviting admins, members, and treasurers into a tenant
- Admin invitation endpoints and frontend invite form
- Accept-invitation flow with initial password setup
- Forgot password / reset password request and confirmation flow
- Password reset token storage and expiry rules
- Optional TOTP-based MFA foundation for admin accounts
- Admin session review/log out other sessions capability or session invalidation baseline
- Basic login abuse protection strategy documented and implemented where reasonable
- Backend tests for invitation acceptance, token expiry, password reset, and auth edge cases
- Frontend screens for invitation acceptance and password reset

Detailed implementation slices:

- Invitation lifecycle
  - define persistent invitation records with tenant scope, target email, role intent, issuer, expiry, and acceptance status
  - design secure invitation acceptance rules for existing users versus brand-new users
  - decide whether invitation acceptance creates a user, binds an existing user, or both depending on email ownership
- Password recovery lifecycle
  - add reset request endpoint with non-enumerating response semantics
  - store reset tokens securely with expiry and one-time-use behavior
  - implement reset confirmation flow with password policy validation
- Authentication hardening
  - introduce baseline password strength policy and clearer failure states
  - add optional MFA scaffolding for privileged accounts without breaking non-MFA tenants
  - define session invalidation behavior for password changes, admin actions, or suspicious account events
- Admin UX
  - add invitation management visibility for admins
  - add acceptance and recovery screens that are explicit, resilient, and understandable
  - expose only safe operational detail, never token secrets
- Security and abuse controls
  - apply sane throttling or lockout guidance for login and reset flows
  - make sure expired, revoked, reused, or cross-tenant tokens fail safely
  - ensure invitation acceptance cannot escalate privilege beyond the inviter's allowed scope

Validation requirements:

- backend tests for invite creation, invite acceptance, duplicate invite handling, reset request, reset confirm, token expiry, token replay, and tenant isolation
- frontend tests for invitation acceptance, invalid token states, and password reset UX
- security review of auth responses to avoid account enumeration and privilege escalation

Definition of done:

- admins can onboard users without manual database work
- users can recover access without unsafe shortcuts
- privileged auth flows are materially stronger than the current baseline
- docs clearly explain invitation and recovery behavior for future agents and operators

Acceptance criteria:

- an admin can invite a user without manual DB intervention
- an invited user can join the tenant through a secure token flow
- a user can reset a forgotten password without direct admin support
- expired or invalid tokens are safely rejected
- admin accounts have a stronger authentication path than the current baseline

## Sprint 18 - Module Enforcement And Entitlements

Status: Completed

Goal:
Make tenant module toggles real product controls instead of configuration-only metadata.

Why this sprint now:

- Sprint 15 introduced module configuration, but without enforcement the feature is not trustworthy.
- Commercial packaging and editioning later in the roadmap require real entitlements, not cosmetic toggles.
- This sprint closes a security and consistency gap between admin settings and runtime behavior.

Primary dependencies:

- Tenant settings and module toggle data from Sprint 15
- Tenant-aware frontend shell from Sprint 16

Execution scope:

- backend enforcement layer
- frontend route and navigation enforcement
- consistency rules for disabled features with existing data
- tests for denial behavior and tenant safety

Deliverables:

- Central backend dependency or policy guard enforcing module availability per tenant
- Router-level protection for disabled modules (`membership`, `contributions`, `policies`, `disciplinary`, `events`, `announcements`, `chat`, `notifications`)
- Consistent 403/404/409 behavior for disabled module access
- Frontend route guards and navigation filtering aligned with backend enforcement
- Health and tenant settings surfaces showing current effective module map
- Admin UX warnings before disabling modules with existing data
- Tests covering disabled module enforcement across API and frontend navigation
- Documentation describing module toggle semantics and operational caveats

Detailed implementation slices:

- Backend enforcement model
  - define a reusable per-module enforcement dependency or policy utility
  - map every module router and sensitive endpoint to a canonical module key
  - decide and document whether disabled modules return 403, 404, or conflict-style responses per case
- Frontend enforcement model
  - align route guards, navigation visibility, and dashboard cards with backend module state
  - prevent dead-end routes and confusing UI states when a module is disabled after a user already visited it
  - ensure the app refresh path re-evaluates enabled modules before rendering protected views
- Operational rules
  - warn admins before disabling a module that already contains business data
  - document whether disabling a module hides data temporarily or requires archival/export steps first
  - preserve tenant data integrity even when a module becomes disabled
- Entitlement foundations
  - keep implementation generic enough to support future edition/package controls
  - avoid scattering toggle checks manually across unrelated code paths
  - centralize module constants and capability mapping

Validation requirements:

- backend tests for every guarded module endpoint in enabled and disabled states
- frontend tests for route denial, navigation filtering, and stale route recovery
- manual validation that direct URL entry cannot bypass a disabled module

Definition of done:

- module toggles alter both backend behavior and frontend visibility
- no disabled feature remains reachable solely through direct routing
- the codebase has a single coherent enforcement pattern reusable by future modules

Acceptance criteria:

- disabling a module prevents access to its API endpoints for that tenant
- disabled modules disappear from the frontend navigation and settings-derived UI
- backend and frontend enforcement stay consistent
- no tenant can accidentally access a disabled feature through a direct URL alone

## Sprint 19 - Audit Trail And Administrative Governance

Status: Completed

Goal:
Introduce a serious administrative audit layer for sensitive product actions beyond chat traceability.

Why this sprint now:

- As modules mature, administrative accountability becomes essential for customer trust and supportability.
- Commercial customers will expect durable evidence for who changed what and when.
- This sprint also reduces future debugging cost by adding operational traceability.

Primary dependencies:

- Stable core CRUD modules from Sprints 3 through 18
- Tenant isolation and admin surfaces already in place

Execution scope:

- structured audit model
- reusable audit emission service
- admin review and export tooling
- tenant-isolated governance workflows

Deliverables:

- Audit log model for sensitive actions across documents, access changes, memberships, contributions, disciplinary actions, settings, and notifications
- Reusable audit service for structured action logging
- Audit events for create/update/delete flows on sensitive business records
- Admin audit review API with filtering by actor, action type, date range, and entity type
- Frontend admin audit screen for operational review
- Export capability for audit results (CSV or JSON baseline)
- Tests covering audit generation for key actions and tenant isolation of logs
- Documentation defining which actions are auditable and why

Detailed implementation slices:

- Audit domain model
  - define durable audit record structure with actor, tenant, action, entity type, entity id, timestamp, result, and redacted context
  - decide which contextual fields are safe to retain and which must be minimized
  - ensure audit storage is append-oriented and resistant to accidental silent mutation
- Emission strategy
  - integrate audit logging into create, update, delete, membership, permission, settings, and document access flows
  - avoid copy-paste audit logic by introducing a small service or utility layer
  - define behavior for failed operations, partial success, and permission-denied attempts where appropriate
- Admin review surface
  - add filtered search by actor, action family, entity type, and date range
  - support practical export for incident review or client reporting
  - make sure no raw sensitive payloads are exposed unnecessarily in the UI
- Governance considerations
  - preserve strict tenant isolation
  - document audit coverage limits so customers are not misled
  - keep audit terminology consistent across backend, frontend, and docs

Validation requirements:

- backend tests proving audit creation for sensitive write operations
- tenant isolation tests for audit review and export
- frontend smoke coverage for audit filtering and export initiation

Definition of done:

- major sensitive admin actions produce durable, queryable audit evidence
- audit review is usable without database access
- audit coverage and exclusions are explicit in the documentation

Acceptance criteria:

- sensitive admin actions generate durable audit records
- tenant A cannot view tenant B audit events
- admins can search and review audit history without raw database access
- audit entries include actor, action, timestamp, and target context

## Sprint 20 - Document Operations Maturity

Status: Completed

Goal:
Make document ingestion and knowledge base operations robust enough for routine business use.

Why this sprint now:

- Kairo's AI value depends on reliable document operations, but ingestion is still operationally shallow in key areas.
- OCR, retry handling, and bulk import are important before commercial deployments or migration projects.
- This sprint strengthens the platform's core knowledge pipeline before broader packaging work.

Primary dependencies:

- Existing upload, ingestion, and indexing foundations from Sprints 3 to 7
- Audit/governance improvements from Sprint 19 where relevant for operator actions

Execution scope:

- OCR and richer ingestion lifecycle
- bulk upload and operator recovery workflows
- diagnostics and duplicate awareness
- realistic tests for ingestion resilience

Deliverables:

- OCR implementation replacing the current placeholder for image-based documents
- Bulk document upload workflow with progress and partial failure reporting
- Retry/requeue ingestion actions for failed jobs
- Better ingestion diagnostics (parser failure reasons, chunk counts, indexing counts)
- Document archive/unarchive lifecycle instead of upload-only/ready semantics
- Optional duplicate detection baseline using checksum and filename heuristics
- Retention or cleanup strategy for superseded document versions
- Tests covering OCR path, bulk upload edge cases, retries, and archive behavior
- Documentation for document operations and operator troubleshooting

Detailed implementation slices:

- OCR enablement
  - replace placeholder image-ingestion behavior with a real OCR pipeline or clearly modular OCR adapter
  - define supported file/image types and failure semantics
  - preserve traceability between uploaded file, extracted text, and chunked/indexed output
- Bulk operations
  - support multi-file submission with per-file status reporting
  - handle partial success cleanly without collapsing the whole batch
  - provide usable operator feedback for failures, duplicates, or skipped items
- Recovery workflows
  - add retry or requeue operations for failed ingestion jobs
  - expose actionable failure diagnostics rather than opaque status labels
  - define archive/unarchive semantics that do not break citation or retrieval history unexpectedly
- Operational maturity
  - add checksum and lightweight duplicate detection heuristics
  - define retention or cleanup expectations for versioned or superseded documents
  - ensure archived or failed documents behave predictably in retrieval and admin listings

Validation requirements:

- backend tests for OCR path, retry flow, duplicate heuristics, archive state transitions, and tenant isolation
- worker/integration validation for ingestion status transitions
- browser or UI smoke checks for bulk upload workflow and recovery actions

Definition of done:

- image-based documents can become searchable through an actual ingestion path
- admins can diagnose and recover failed ingestion runs without direct database intervention
- document lifecycle states are understandable, durable, and reflected in the UI

Acceptance criteria:

- image-based uploads can produce searchable text through OCR
- admins can recover from failed ingestion without manual database intervention
- bulk upload is usable for real tenant setup and migration work
- document lifecycle is clearer than the current minimal status model

## Sprint 21 - Data Import And Backoffice Automation

Status: Completed

Goal:
Reduce manual administration effort with structured import/export workflows for core business records.

Why this sprint now:

- After document operations mature, the next business bottleneck is manual data entry for real customer onboarding.
- Commercial rollout requires practical migration paths from spreadsheets and legacy office processes.
- This sprint transforms the product from demo-friendly to operations-friendly.

Primary dependencies:

- Membership and contributions modules from Sprint 8
- Stable tenant UX from Sprint 16
- Stronger governance from Sprint 19 for import traceability where needed

Execution scope:

- member and contribution import pipelines
- dry-run validation and reporting
- exports for operational reporting
- admin-friendly import UX with safe failure handling

Deliverables:

- CSV import for member profiles replacing the current placeholder
- CSV or spreadsheet import for contribution records
- Validation report format for import errors and warnings
- Dry-run import mode before persistence
- Export endpoints for members, contributions, events, and announcements
- Admin frontend import screens with upload, validation summary, and result review
- Tests for malformed rows, duplicates, tenant isolation, and dry-run safety
- Documentation for supported import templates and operational workflow

Detailed implementation slices:

- Import architecture
  - define import parsing, validation, normalization, and persistence phases explicitly
  - support dry-run mode that produces a useful report without writing records
  - design row-level error reporting that operators can act on without reading server logs
- Member import
  - replace placeholder logic with real CSV/spreadsheet mapping for core profile fields
  - handle duplicates, missing required fields, and identifier collisions predictably
  - decide how imports interact with existing users versus profile-only records
- Contribution import
  - support expected amounts, payment history baselines, or partial settlement data as appropriate
  - validate year, amount, currency assumptions, and member matching rules
  - ensure financial imports do not silently corrupt balance calculations
- Export workflows
  - provide clean tenant-scoped exports for members, contributions, events, and announcements
  - choose stable column naming and formatting conventions
  - ensure exported data respects role and tenant boundaries

Validation requirements:

- backend tests for dry-run behavior, duplicate handling, malformed files, and cross-tenant safety
- frontend tests for import summary rendering and failure reporting
- sample import templates validated against the implemented parser

Definition of done:

- admins can move meaningful operational data in and out of Kairo without bespoke scripts
- bad rows are isolated and reported clearly
- dry-run mode is trustworthy enough to use before real imports

Acceptance criteria:

- an admin can import member and contribution data without manual API scripting
- invalid rows are reported clearly without corrupting valid data
- imports are tenant-scoped and reversible where appropriate
- exports produce useful operational data for external reporting

## Sprint 22 - Product UX Polish And Browser QA

Status: Complete

Goal:
Raise the user experience from functional admin tooling to a polished, trustworthy product surface.

Why this sprint now:

- By this point, the main product modules should exist, making end-to-end UX refinement efficient.
- Commercial perception is shaped heavily by reliability, clarity, and consistency in daily workflows.
- This sprint also prepares the product for higher-confidence demos and acceptance testing.

Primary dependencies:

- Stable flows across Sprints 16 through 21
- Existing frontend surface and component library patterns

Execution scope:

- cross-flow UX cleanup
- accessibility and responsive quality pass
- browser-level regression coverage
- clearer role-aware messaging and state handling

Deliverables:

- [x] Workflow review: error/loading/empty states standardized across 4 first-gen admin views
- [x] UX copy cleanup: "Export CSV" / "Cancel" labels aligned across admin views
- [x] Responsive fixes: offcanvas mobile sidebar for AppLayout and AdminLayout
- [x] Role-aware UI: Admin link hidden from non-admin users in AppLayout sidebar
- [x] Browser-based end-to-end smoke test suite: Playwright config + unauthenticated-flow specs written (need running stack to execute)
- [x] Accessibility pass: ARIA labels, focus-visible styles, scope attributes, modal labelling
- [x] Frontend component cleanup: export blob logic extracted to `useCsvExport` composable

Detailed implementation slices:

- Workflow review
  - review the full user journey for admins, members, and treasurers across major modules
  - remove dead ends, ambiguous labels, and inconsistent page-level behaviors
  - align empty states and success/error messaging with real product expectations
- Accessibility and responsiveness
  - improve semantic labels, keyboard navigation, focus handling, color contrast, and screen-size behavior
  - validate tables, forms, modals, badges, and alerts across desktop and mobile widths
  - ensure branded elements remain readable and professional
- Frontend maintainability
  - reduce fragile page-level API coupling where views have accumulated too much orchestration logic
  - standardize loading and error state patterns
  - keep changes coherent with the current Vue architecture instead of introducing a UI rewrite
- Browser QA
  - add browser-level smoke flows for login, tenant selection, documents, chat, members, contributions, policies, events, and settings
  - focus on critical customer-visible regressions rather than broad but shallow coverage
  - capture stable setup instructions so future agents can rerun the suite consistently

Validation requirements:

- browser smoke suite for critical flows
- frontend tests for key shared UI states where practical
- manual responsive verification on desktop, tablet, and mobile breakpoints

Definition of done:

- the product feels coherent and reliable across its main workflows
- browser-level smoke tests cover the most commercially important flows
- obvious accessibility and responsive quality issues are materially reduced

Acceptance criteria:

- the major product workflows are reliable on desktop and mobile
- accessibility and error recovery are materially better than the current baseline
- critical flows are covered by automated browser-level smoke tests
- the UI looks and behaves like a professional product, not just an internal tool

## Sprint 23 - Observability And Runtime Reliability

Status: Completed

Goal:
Give operators and future customers enough visibility to trust the system in daily use.

Why this sprint now:

- After the surface is polished, operational trust becomes the next barrier to production adoption.
- Support and incident response become difficult without metrics, health quality, and correlation across components.
- This sprint lowers operating risk before production validation work.

Primary dependencies:

- Mature application flows through Sprint 22
- Existing `/health`, worker, and infrastructure foundations

Execution scope:

- runtime observability primitives
- health and dependency introspection
- background job visibility
- operational documentation for support and diagnosis

Deliverables:

- Metrics endpoint or observability integration for API, worker, queue, ingestion, and chat flows
- Structured error taxonomy and correlation IDs across request lifecycles
- Background job health visibility (queued, processing, failed, retried)
- Optional runtime dashboards or example Grafana/Prometheus integration docs
- Alerting guidance for critical failure modes (DB unavailable, worker stuck, ingestion backlog)
- Better health probes for Redis, MinIO, Qdrant, and Ollama
- Tests for health response shape and degraded dependency reporting
- Operations documentation for logs, metrics, and troubleshooting

Detailed implementation slices:

- Metrics and telemetry
  - define practical metrics for API latency, error rates, ingestion throughput, job failures, and chat usage
  - keep the initial observability layer simple enough to operate locally and in small deployments
  - expose metrics in a format that can support future dashboards or managed monitoring
- Correlation and error taxonomy
  - add request or operation correlation identifiers where they materially improve debugging
  - normalize key error classes so logs and support diagnostics are easier to interpret
  - avoid leaking sensitive content into logs
- Dependency health
  - improve `/health` so it reflects real dependency state rather than a shallow process-up signal
  - include Redis, MinIO, Qdrant, Ollama, and worker/queue visibility where feasible
  - clearly separate healthy, degraded, and unavailable states
- Supportability
  - document how operators inspect queues, failed jobs, ingestion backlog, and degraded dependencies
  - provide example dashboard or monitoring integration guidance without overengineering
  - make sure support teams can reason from symptoms to likely subsystem

Validation requirements:

- backend tests for health response contract and degraded dependency states
- manual validation of metrics exposure and worker/dependency diagnostics
- documentation review for real incident workflows

Definition of done:

- operators can determine whether the platform is healthy, degraded, or failing
- support diagnostics no longer depend on reading source code first
- runtime visibility covers both request path and background processing path

Acceptance criteria:

- operators can detect degraded dependencies quickly
- API and worker runtime have actionable observability beyond raw logs
- health reporting reflects the real state of critical services
- support teams can diagnose common incidents without reading code

## Sprint 24 - Production Validation, Recovery And Security Hardening

Status: Completed

Goal:
Prove that the platform is not only designed for production, but actually survivable in production-like conditions.

Why this sprint now:

- Observability helps detect problems, but commercial readiness also requires recovery and hardening evidence.
- This sprint is where documented production posture becomes validated operational practice.
- It reduces deployment risk before positioning the product as commercially launchable.

Primary dependencies:

- Deployment and backup docs from Sprint 11
- Observability and health improvements from Sprint 23

Execution scope:

- production-like deployment validation
- restore and upgrade drills
- auth and sensitive-route hardening
- security and supply-chain review baseline

Deliverables:

- End-to-end production Docker validation runbook and repeatable smoke test
- Restore drill documentation and validation for backups
- Upgrade/migration runbook for schema and application releases
- Secret rotation guidance and environment hardening improvements
- Admin route protection hardening recommendations or baseline implementation
- Optional rate limiting baseline for auth and sensitive endpoints
- Dependency review and supply-chain hardening pass
- Security regression tests or checklists for production-sensitive flows

Detailed implementation slices:

- Production validation
  - perform a repeatable production-like deployment check using the documented Docker flow
  - verify frontend build, API startup, worker startup, storage integration, and essential user journeys
  - capture the exact operational steps required to reproduce the validation
- Recovery and continuity
  - validate backup and restore guidance with at least one practical restore drill
  - define what constitutes a successful recovery for database, objects, and vector state
  - identify any unrecoverable gaps and document them honestly
- Upgrade safety
  - document and test schema/application upgrade expectations with rollback considerations where realistic
  - make migration risk visible instead of assumed
  - ensure future agents have a runbook for safe product evolution
- Security hardening
  - review auth, admin, and sensitive endpoints for the most obvious production gaps
  - add baseline rate limiting or mitigation where justified
  - review dependency posture and configuration hardening without derailing the existing architecture

Validation requirements:

- production-like smoke run
- restore drill evidence
- security checklist or regression tests for critical routes and auth flows

Definition of done:

- recovery and deployment guidance are validated, not just aspirational
- the most obvious production hardening gaps are either fixed or explicitly bounded
- operators have practical runbooks for deployment, restore, and upgrade workflows

Acceptance criteria:

- production build and restore workflow are validated, not just documented
- upgrade path is explicit enough for a real customer deployment
- the most obvious production security gaps are closed or clearly bounded
- operators can recover from common failure scenarios with documented steps

## Sprint 25 - Commercial Packaging And Launch Readiness

Status: Completed

Goal:
Turn Kairo from a strong engineering product into a sellable and supportable commercial offer.

Why this sprint now:

- Product and platform maturity alone do not make a commercial offer understandable or supportable.
- A final packaging sprint is needed to turn engineering readiness into buyer clarity and operator confidence.
- This sprint defines the bridge from product prototype to commercial MVP.

Primary dependencies:

- Stable product surface through Sprint 24
- Deployment, support, security, and operational docs already validated

Execution scope:

- commercial packaging definition
- support and onboarding materials
- demo-to-production transition guidance
- final readiness review from a product-business perspective

Deliverables:

- Product packaging definition: self-hosted edition, managed-service edition, and support boundaries
- Final product README and positioning refresh for commercial conversations
- Customer-facing onboarding documentation and administrator guide
- Support playbook for installation, upgrades, incidents, and common questions
- Feature matrix clarifying included modules, optional channels, and future premium connectors
- Example pricing/offer structure or commercialization notes for service-led rollout
- Demo-to-production transition checklist
- Final maturity review of legal, branding, support, and operational readiness

Detailed implementation slices:

- Offer definition
  - define what is included in self-hosted versus managed-service positioning
  - clarify support boundaries, customer responsibilities, and implementation expectations
  - make the feature matrix understandable without needing to inspect the repository
- Customer-facing documentation
  - produce a cleaner onboarding path for administrators and evaluators
  - refresh README and positioning language for commercial conversations rather than purely technical review
  - align terminology across docs, UI, and demo material
- Support readiness
  - prepare installation, upgrade, incident, and FAQ guidance that a support workflow can actually use
  - identify which flows are mature, beta, optional, or future-looking
  - document escalation boundaries for integrations and external providers
- Commercial readiness review
  - capture remaining blockers that still separate the product from a confident commercial MVP
  - identify any legal, operational, or branding gaps that require decision rather than engineering
  - define the immediate post-Sprint-25 path for pilot customers or managed onboarding

Validation requirements:

- documentation review from the perspective of a new evaluator and a future operator
- consistency pass across README, deployment docs, onboarding docs, and roadmap status
- final launch-readiness checklist with explicit unresolved items

Definition of done:

- Kairo can be presented as a credible commercial MVP with clear packaging and support boundaries
- a new evaluator can understand what the product is, how it is deployed, and what operational model is offered
- the roadmap after Sprint 25 is no longer foundational maturity, but market expansion or premium evolution

Acceptance criteria:

- a prospect can understand what the product is, how it is deployed, and what they are buying
- the project can be presented as a credible commercial MVP
- support and operational boundaries are explicit enough for real customer conversations
- the path from demo environment to customer environment is clearly documented

## Sprint 26 - Public Product Landing And Lead Capture

Status: Completed

Goal:
Turn the public sign-in experience into a credible product landing surface that communicates value fast without weakening access control.

Why this sprint now:

- The commercial documentation is in place, but the public entry point still looks mostly like a sign-in form.
- Prospects need to understand the product in seconds, not only after opening repository docs.
- A stronger first impression supports demos, pilot conversations, and self-serve evaluation.

Primary dependencies:

- Commercial packaging docs from Sprint 25
- Existing public login route and auth flow
- Frontend branding and responsive shell work from Sprints 2 and 22

Execution scope:

- public-facing login page redesign with a commercial landing narrative
- feature highlights and trust signals for evaluators
- clear call-to-action toward sign-in and commercial docs
- mobile-first layout that still works as the auth entry point
- browser-level regression coverage for the public entry page

Deliverables:

- Redesigned login page with a stronger product value proposition
- Public summary of Kairo capabilities and deployment posture on the login surface
- Prominent trust signals for tenant isolation, citations, and production readiness
- More intentional empty/login states for guests
- E2E coverage for the public entry page and the existing auth redirects
- Documentation note explaining the public entry surface

Detailed implementation slices:

- Landing experience
  - present Kairo as a product, not only a form
  - explain the main value pillars: private AI, operational workflows, production posture
  - keep the actual sign-in path obvious and fast
- Visual credibility
  - use a layout that feels intentionally commercial and professional
  - make the mobile view readable and not cramped
  - preserve the established brand language and tenant-aware styling
- Safety and continuity
  - keep backend auth unchanged
  - do not expose private tenant data on the public page
  - ensure authenticated users still land in the app, not on the marketing surface
- Validation
  - update browser checks for the public entry surface
  - verify login, tenant selection, and protected redirects still work

Validation requirements:

- frontend build passing
- browser smoke coverage for the public entry page
- no regression in login or authenticated route guards

Definition of done:

- a first-time visitor can understand what Kairo does before signing in
- the login page reads like a product entry point, not a bare authentication form
- authenticated users still reach the app normally

Acceptance criteria:

- the public entry page explains the product value in a few seconds
- the sign-in path remains clear and working
- the surface looks credible enough for a live evaluation demo

Completed implementation:

- `apps/web/src/views/auth/LoginView.vue` now presents a commercial hero section, trust signals, and a clear sign-in card without changing backend auth rules
- `apps/web/e2e/login.spec.ts` now validates the public entry surface and the existing redirect behavior
- Frontend build passed and Playwright login smoke coverage passed on Chromium

## Sprint 27 - Guided Tenant Onboarding And Conversion Flow

Status: Completed

Goal:
Help a new tenant admin move from login to a working environment with less confusion and fewer dead ends.

Why this sprint now:

- Once the public entry is better, the next gap is first-time tenant orientation.
- A commercial offer should help evaluators become productive quickly.
- The current product still assumes too much prior knowledge after login.

Primary dependencies:

- Sprint 26 public entry surface
- Existing tenant settings, module toggles, and multi-tenant auth flow
- Existing empty states and onboarding-adjacent docs

Execution scope:

- first-run checklist or onboarding guidance inside the app
- clearer next-step cues after tenant login
- conversion from demo thinking to real tenant setup
- tighter empty states for brand-new tenants

Deliverables:

- Guided first-run checklist for new tenant admins
- Clear next-step guidance after login when a tenant has little or no data
- Updated empty states that point toward setup actions
- Documentation for the evaluator-to-admin transition

Validation requirements:

- browser validation for first login and first-run orientation
- tests for empty-state and tenant-setup guidance

Definition of done:

- a new tenant admin can orient themselves quickly after first login
- the product suggests useful next steps without exposing sensitive internals

Acceptance criteria:

- the app helps new customers move from demo to working setup
- empty states and first-run guidance feel intentional and helpful

Completed implementation:

- `apps/web/src/composables/useTenantOnboarding.ts` now derives a first-run checklist from real tenant signals instead of static copy
- `apps/web/src/views/dashboard/DashboardView.vue` now presents setup progress, next best action, quick actions, and tenant usage metrics
- `apps/web/src/views/admin/AdminDocumentsView.vue` and `apps/web/src/views/members/AdminMembersView.vue` now expose setup-oriented empty states with direct actions
- `docs/commercial/onboarding-guide.md` and `docs/commercial/feature-matrix.md` now describe the guided onboarding surface
- `apps/web/playwright.config.ts`, `apps/web/e2e/login.spec.ts`, and `apps/web/e2e/dashboard.spec.ts` now provide autonomous browser validation without requiring a local backend

## Sprint 28 - Admin Overview And Tenant Operations Hub

Status: Completed

Goal:
Replace the placeholder admin home with a real operations hub that helps tenant admins monitor readiness, activity, and risk in one place.

Why this sprint now:

- Sprint 27 improves first-run guidance, but `/admin` is still a Sprint 2 placeholder and weakens the product's commercial credibility.
- Tenant admins need a command surface that summarizes operational status without jumping across multiple modules.
- This sprint converts an obvious maturity gap into a product-strengthening surface for demos and day-to-day use.

Primary dependencies:

- Sprint 27 guided onboarding dashboard
- Existing observability, audit, document, member, contribution, event, announcement, and notification modules
- Tenant settings and module toggles already enforced in the shell

Execution scope:

- real admin overview data cards and summaries
- launch-readiness and operational health indicators
- shortcuts into the highest-value admin workflows
- module-aware admin overview rendering

Deliverables:

- Real `AdminOverviewView` replacing placeholder sprint text
- Summary cards for documents, members, contributions, announcements, events, and audit activity where enabled
- Admin-oriented readiness or risk panel surfacing missing setup items and operational warnings
- Quick links into documents, settings, members, announcements, events, audit, and notification diagnostics
- Module-aware hiding of overview widgets for disabled modules
- Browser and frontend validation for the new admin hub
- Documentation update for the admin operating surface

Validation requirements:

- frontend build passing
- browser validation for authenticated admin overview rendering
- no regression in admin routing and module-aware visibility

Definition of done:

- `/admin` no longer feels like a placeholder
- a tenant admin can understand current readiness and the next operational action from one screen
- the view respects module toggles and tenant isolation

Acceptance criteria:

- the admin landing page surfaces real product state
- disabled modules do not render misleading cards
- the page is credible enough for demo and production handoff conversations

Completed implementation:

- `apps/web/src/views/admin/AdminOverviewView.vue` now replaces the placeholder with a real admin operations hub
- `apps/web/src/composables/useAdminOverview.ts` aggregates documents, members, contributions, events, announcements, audit, channels, ingestion health, and onboarding readiness into one surface
- `apps/web/src/api/admin.api.ts` adds the frontend contract for ingestion job health
- `apps/web/src/layouts/AdminLayout.vue` and `apps/web/src/layouts/AppLayout.vue` now react correctly to module-state changes instead of freezing module visibility at first render
- `apps/web/e2e/admin-overview.spec.ts` now validates the authenticated admin hub and module-aware hiding through autonomous browser mocks
- `docs/commercial/administrator-guide.md` now documents the admin overview as an operations hub

## Sprint 29 - Team Invitations And Access Operations Console

Status: Completed

Goal:
Turn the existing invitation and identity lifecycle backend into a credible admin-facing operations workflow for onboarding real customer teams.

Why this sprint now:

- The admin landing page is now useful, but tenant administrators still lack a strong in-product surface to invite colleagues and manage access lifecycle.
- The backend foundations for invitations, MFA, and password recovery already exist, so the highest-value next step is operationalizing them in the admin UX.
- Commercial deployments need team onboarding to feel first-class, not hidden behind API capability alone.

Primary dependencies:

- Sprint 17 identity lifecycle backend
- Sprint 28 admin operations hub
- Existing tenant settings, audit logging, and role model

Execution scope:

- admin invitation management surface
- visibility into pending and completed invitation state
- operational cues around MFA and access lifecycle
- browser and regression validation for access operations

Deliverables:

- Admin UI for inviting users into a tenant with role selection
- Pending invitation list with expiry and cancellation visibility
- Links or flows that connect invitation operations to the broader admin hub
- Better admin-facing access lifecycle guidance for onboarding teammates
- Browser validation for invite-management interactions
- Documentation update for tenant team onboarding and access operations

Validation requirements:

- frontend build passing
- browser validation for admin invitation workflow
- no regression in auth routing, role checks, or tenant isolation assumptions

Definition of done:

- a tenant admin can onboard other users through the product without API-only workflows
- invitation state is visible and understandable from the admin surface
- the product is more credible for real multi-user tenant rollout

Acceptance criteria:

- an admin can initiate and review invitations from the UI
- pending invitations are visible with meaningful status
- the workflow feels coherent with the admin operations hub

Completed implementation:

- `apps/web/src/views/admin/AdminAccessView.vue` now provides a dedicated admin console for team invitations and access rollout
- `apps/web/src/api/settings.api.ts` now loads tenant-scoped roles from the backend for real invite role selection
- `services/api/app/modules/tenancy/router.py` and `services/api/app/modules/tenancy/service.py` now expose an admin-safe tenant roles endpoint used by the access console
- `apps/web/src/layouts/AdminLayout.vue` and `apps/web/src/router/index.ts` now surface the access console in navigation and preserve admin session restoration without premature redirects
- `apps/web/src/composables/useAdminOverview.ts` now links the operations hub directly to access operations
- `apps/web/e2e/admin-access.spec.ts` now validates invitation creation and cancellation autonomously through Playwright mocks
- `services/api/tests/test_multi_tenant_auth.py` now verifies the tenant roles endpoint for both admin and non-admin users
- `docs/commercial/administrator-guide.md`, `PROJECT_STATUS.md`, `docs/ai/NEXT_SPRINT.md`, and `docs/ai/PROJECT_STATE.md` now reflect the new access operations surface

## Sprint 30 - Account Security And Identity Self-Service

Status: Completed

Goal:
Turn the existing MFA, password recovery, and post-invite identity flows into a coherent user-facing security surface suitable for real customer operations.

Why this sprint now:

- Sprint 29 makes team onboarding real, but the day-2 security experience is still fragmented across isolated auth screens.
- Commercial customers need a visible security posture for password recovery, MFA enablement, and account hardening after invitation acceptance.
- The backend foundations already exist, so the next leverage point is productizing them into a coherent self-service experience.

Primary dependencies:

- Sprint 17 identity lifecycle backend
- Sprint 29 access operations console
- Existing audit logging and auth rate limiting

Execution scope:

- authenticated security settings UX
- clearer MFA enrollment and disablement flow
- stronger continuity across invite acceptance, login, forgot-password, and reset-password journeys
- browser and regression validation for identity self-service

Deliverables:

- Dedicated authenticated security view for MFA status, enrollment, verification guidance, and disablement
- Clear navigation path from the product shell into personal account security
- Better continuity messaging between invitation acceptance, login, forgot-password, and reset-password screens
- Browser validation for MFA setup/disable and password-reset journeys through autonomous mocks where possible
- Documentation update for account security operations and user self-service expectations

Validation requirements:

- frontend build passing
- browser validation for MFA and password lifecycle UX
- no regression in auth routing, invite acceptance, or backend-enforced access control

Definition of done:

- a real invited user can move from account creation to a credible self-service security posture
- MFA and password recovery are understandable without reading backend docs
- account-security flows feel like part of the product, not detached utility screens

Acceptance criteria:

- a user can find and manage MFA from within the product
- password recovery and invite acceptance feel consistent and production-ready
- the sprint preserves backend authority for all access and security decisions

Completed implementation:

- `services/api/app/modules/identity/router.py`, `service.py`, and `schemas.py` now expose a minimal MFA status endpoint so the frontend can render account security state without leaking secrets
- `services/api/tests/test_identity_lifecycle.py` now validates MFA status across disabled, enrolled, enabled, and disabled-again scenarios
- `apps/web/src/views/account/AccountSecurityView.vue` now provides an authenticated account security surface for MFA setup, verification, disablement, and password recovery launch
- `apps/web/src/layouts/AppLayout.vue` and `apps/web/src/router/index.ts` now provide a first-class navigation path into account security, and `/mfa/setup` now resolves into the new authenticated security surface
- `apps/web/src/views/auth/AcceptInviteView.vue`, `LoginView.vue`, `ForgotPasswordView.vue`, and `ResetPasswordView.vue` now present clearer continuity around post-login security hardening
- `apps/web/e2e/account-security.spec.ts` now validates MFA enablement, disablement, and password recovery launch autonomously through Playwright mocks
- `docs/commercial/administrator-guide.md`, `PROJECT_STATUS.md`, `docs/ai/NEXT_SPRINT.md`, and `docs/ai/PROJECT_STATE.md` now reflect the new self-service account security surface

## Sprint 31 - Secure Identity Message Delivery And Access Notifications

Status: Completed

Goal:
Replace manual invite and reset-link handoff with a real, auditable outbound identity message pipeline suitable for customer operations.

Why this sprint now:

- Sprint 29 and Sprint 30 made access and security workflows credible inside the product, but message delivery is still the weakest operational gap.
- Commercial deployments need invites and password-recovery notifications to be delivered through a real channel, not only copied manually or surfaced as development tokens.
- The notification abstraction already exists, so the next step is to connect identity lifecycle events to a maintainable delivery path.

Primary dependencies:

- Sprint 14 multi-channel extension foundation
- Sprint 29 access operations console
- Sprint 30 account security self-service flows

Execution scope:

- outbound delivery for invitations and password reset
- operational visibility into delivery success or failure
- branded message baseline for customer-facing identity emails
- tests and docs for delivery behavior

Deliverables:

- Identity message delivery abstraction for invitation and password reset flows
- Initial real email-oriented provider integration or production-ready provider contract replacing manual-only handoff
- Branded baseline templates for invitation and password recovery messages
- Admin visibility into delivery success/failure or fallback state where useful
- Test coverage for successful dispatch, provider failure, and safe fallback behavior
- Documentation for configuring and operating identity message delivery

Validation requirements:

- backend tests for invite/reset delivery behavior and provider-failure safety
- frontend or browser validation where delivery state is surfaced
- no regression in tenant isolation, auth safety, or non-enumeration guarantees

Definition of done:

- identity flows no longer depend on manual link sharing as the primary operational path
- delivery failure states are visible and supportable
- the delivery layer stays modular and subordinate to backend security controls

Acceptance criteria:

- invitation and password reset flows can dispatch through a real configured delivery path
- delivery failures degrade safely without exposing unauthorized data
- operators can understand whether an identity message was sent, simulated, or failed

Completed implementation:

- `services/api/app/providers/notifications/base.py` and `placeholders.py` now support direct identity-message dispatch, with SMTP-backed email delivery when configured and simulated fallback otherwise
- `services/api/app/modules/identity/service.py`, `router.py`, and `schemas.py` now route invitation and forgot-password flows through notification providers, record delivery outcomes, and hide raw tokens after successful production delivery
- `apps/web/src/api/auth.api.ts` and `apps/web/src/views/admin/AdminAccessView.vue` now expose and render delivery-state feedback for the latest invitation instead of assuming manual link sharing is always required
- `services/api/tests/test_identity_delivery.py` now validates sent, simulated, and failed delivery behavior with autonomous fake providers and production-mode token-hiding assertions
- `apps/web/e2e/admin-access.spec.ts` now validates the updated access-console delivery UX through Playwright mocks
- Verified with:
  - `python -m pytest services/api/tests/test_identity_lifecycle.py services/api/tests/test_identity_delivery.py services/api/tests/test_notifications.py -q`
  - `npm run build`
  - `npx playwright test e2e/admin-access.spec.ts --config=playwright.config.ts --reporter=line`

## Sprint 32 - Session Governance And Security Event Operations

Status: Completed

Goal:
Turn identity security from individual flows into an operationally mature session-governance model for users and tenant administrators.

Why this sprint now:

- Sprint 31 closes outbound identity delivery, but commercial operators still lack strong visibility and control over active sessions and suspicious account activity.
- Password reset, MFA, and invite flows are now credible, so the next maturity gap is post-authentication governance.
- Security-conscious customers expect session revocation, recent-security-event visibility, and safer recovery after sensitive account changes.

Primary dependencies:

- Sprint 17 identity lifecycle foundation
- Sprint 19 audit trail and governance
- Sprint 30 account security surface
- Sprint 31 identity delivery pipeline

Execution scope:

- session inventory and revocation controls
- security-event visibility for users and admins
- safer token invalidation after sensitive identity changes
- regression-safe backend and browser validation

Deliverables:

- Backend session model or equivalent token-version strategy for revoking active sessions safely
- User-facing session visibility in the authenticated security area, including current session identification
- Logout-other-sessions and logout-all-sessions controls with backend enforcement
- Automatic session invalidation rules after password reset, MFA disablement, or administrator-driven account lockdown where appropriate
- Admin and/or user-visible recent security events based on the audit trail for critical identity actions
- Tests for session revocation, refresh-token invalidation, multi-tenant safety, and browser-level UX continuity
- Documentation for session governance and incident response workflow

Validation requirements:

- backend tests for session revocation and sensitive-identity-event invalidation
- frontend build and browser validation for the account-security session controls
- no regression in tenant isolation, backend-only authorization, or auth recovery flows

Definition of done:

- users and operators can see and revoke active access paths with confidence
- sensitive account changes invalidate stale sessions consistently
- security operations move beyond one-off identity flows into a maintainable commercial posture

Acceptance criteria:

- a user can identify and revoke other active sessions from the product
- password reset or similar sensitive actions invalidate stale sessions according to policy
- administrators and support operators can review recent critical identity events without bypassing backend controls

Completed implementation:

- `services/api/app/modules/identity/models.py` and `repository.py` now add a persistent `UserSession` inventory used for backend-enforced session validation and revocation
- `services/api/app/core/security.py` and `core/dependencies.py` now carry `sid` inside access and refresh JWTs so revoked sessions are rejected by the backend on every authenticated request
- `services/api/app/modules/identity/service.py`, `router.py`, and `schemas.py` now expose session inventory, per-session revocation, revoke-other-sessions, revoke-all-sessions, and current-user security-event endpoints
- Password reset completion now revokes all active sessions for the user, and MFA disablement now revokes other sessions while preserving the current request path
- Successful logins and session revocations are now recorded in the identity audit trail so the authenticated user and tenant admins can review security-relevant events
- `apps/web/src/views/account/AccountSecurityView.vue` now surfaces active sessions, revoke controls, and recent security activity alongside MFA and password recovery
- `services/api/tests/test_session_governance.py` now covers session inventory, targeted revocation, global revocation, password-reset invalidation, refresh-token invalidation, and MFA-disable side effects
- `apps/web/e2e/account-security.spec.ts` now validates the session-governance UX through autonomous Playwright mocks
- Verified with:
  - `python -m pytest services/api/tests/test_auth.py services/api/tests/test_identity_lifecycle.py services/api/tests/test_identity_delivery.py services/api/tests/test_session_governance.py -q`
  - `npm run build`
  - `npx playwright test e2e/account-security.spec.ts --config=playwright.config.ts --reporter=line`

## Final Open-Source Stabilization Track

Strategic target:
Ship Kairo as a stable, portfolio-grade open-source product that is realistic to operate for an association or organization of about 200 members.

Delivery constraint:
The remaining roadmap is intentionally capped at five execution sprints, from Sprint 33 through Sprint 37.

Priority rule for these final sprints:

1. secure user lifecycle and tenant governance
2. harden authentication and session behavior
3. reduce operational fragility and migration risk
4. strengthen real association-facing workflows
5. finish with stability, docs, and demonstrable open-source readiness

## Sprint 33 - Tenant User Lifecycle Governance And Account Lockdown

Status: Completed

Goal:
Give tenant administrators safe operational control over user lifecycle state, access suspension, and identity incident response.

Why this sprint now:

- Sprint 32 gives users session visibility and revocation, but administrators still cannot directly suspend or contain risky accounts inside the product.
- For a stable organization-ready release, offboarding and account containment must be first-class product behavior rather than manual database work.
- The audit trail, invitation flow, and session inventory are now mature enough to support admin lifecycle actions without bypassing backend policy.

Primary dependencies:

- Sprint 17 identity lifecycle foundation
- Sprint 19 audit trail and governance
- Sprint 29 access operations console
- Sprint 32 session governance and security event operations

Execution scope:

- admin-visible user lifecycle state and access status
- account suspension or deactivation with backend enforcement
- tenant-scoped forced session revocation for incident response
- stronger admin visibility into identity events and risky states

Deliverables:

- Admin user-access management view or extension of the access console showing active, invited, suspended, and disabled account states
- Backend endpoints for tenant-authorized suspension, reactivation, and forced session revocation of managed users
- Clear backend rules for what happens to authentication, session access, and invitation reuse when an account is suspended
- Audit coverage for admin-driven account lifecycle actions and forced revocations
- Frontend workflows for safe confirmation of suspension/reactivation actions
- Tests for admin enforcement, tenant isolation, suspended-user denial, and incident-response flows
- Documentation for offboarding and account-compromise response

Validation requirements:

- backend tests for suspension/reactivation/session containment
- frontend build and browser validation for admin lifecycle operations
- no regression in invitation flow, session governance, or backend-only access control

Definition of done:

- tenant admins can contain a compromised or departed user without database-only intervention
- suspended accounts lose effective access through backend enforcement and session invalidation
- lifecycle governance becomes supportable for real tenant operations

Acceptance criteria:

- an admin can suspend or reactivate a tenant user through the product
- suspension invalidates active access safely and predictably
- all admin lifecycle actions remain tenant-scoped, audited, and backend-enforced

Completed implementation:

- `services/api/app/core/dependencies.py` now revalidates the active tenant membership on every protected request, so suspended memberships lose backend access immediately instead of only failing on the next login
- `services/api/app/modules/tenancy/repository.py` now exposes tenant-user detail listing and explicit membership-status updates for lifecycle operations
- `services/api/app/modules/identity/repository.py` now supports tenant-scoped active-session counting and tenant-scoped session revocation for managed users
- `services/api/app/modules/identity/service.py`, `router.py`, and `schemas.py` now expose admin lifecycle endpoints for managed-user listing, suspension, reactivation, and forced tenant-session revocation
- Invitation handling now blocks reuse as a reactivation bypass: existing suspended or historical memberships must be managed through lifecycle controls instead of a fresh invite
- `apps/web/src/api/auth.api.ts` and `apps/web/src/views/admin/AdminAccessView.vue` now extend `/admin/access` into a combined onboarding and lifecycle console with membership status, active-session counts, recent identity activity, suspend/reactivate actions, and forced session revocation
- `services/api/tests/test_identity_governance.py` now validates admin-only lifecycle management, tenant isolation, self-protection rules, suspended-user denial, reactivation, and tenant-scoped session containment
- `apps/web/e2e/admin-access.spec.ts` now validates lifecycle actions through autonomous Playwright mocks in addition to invitation flows
- Verified with:
  - `python -m pytest services/api/tests/test_identity_lifecycle.py services/api/tests/test_identity_delivery.py services/api/tests/test_session_governance.py services/api/tests/test_identity_governance.py -q`
  - `npm run build`
  - `npx playwright test e2e/admin-access.spec.ts --config=playwright.config.ts --reporter=line`

## Sprint 34 - Authentication Hardening And Recovery Stability

Status: Completed

Goal:
Make login, recovery, invitation acceptance, and session continuity resilient enough for daily use without hidden auth edge-case failures.

Why this sprint now:

- Once admins can suspend and reactivate accounts, authentication state transitions become more complex and easier to regress.
- A portfolio-grade open-source release must be stable around the most frequently used flows: sign-in, invite acceptance, password reset, session refresh, and logout.
- This sprint turns identity from feature-complete into predictably supportable behavior.

Primary dependencies:

- Sprint 30 account security and identity self-service
- Sprint 31 secure identity delivery
- Sprint 32 session governance
- Sprint 33 tenant lifecycle governance

Execution scope:

- auth edge-case stabilization
- invitation and reset-token lifecycle consistency
- better defensive handling of expired, replayed, revoked, and cross-state credentials
- stronger browser and API regression coverage for authentication-critical flows

Deliverables:

- Hardened backend handling for revoked, expired, already-used, or state-incompatible identity tokens
- Clear user-facing frontend states for expired invites, revoked access, locked accounts, and invalid reset links
- Additional backend tests around auth transitions, replay attempts, and state invalidation rules
- Additional Playwright coverage for login, accept-invite, forgot-password, reset-password, logout, tenant switching, and suspended-user denial
- Documentation of supported identity state transitions and recovery expectations

Validation requirements:

- targeted backend auth and identity tests all pass
- frontend build passes
- browser validation covers the main auth journeys without relying on a local PostgreSQL instance

Definition of done:

- authentication and recovery flows fail safely and predictably under edge conditions
- identity regressions become easier to catch automatically before later sprint work

Acceptance criteria:

- expired or replayed tokens always produce safe backend-enforced outcomes
- suspended or disabled users cannot bypass restrictions through stale sessions or incomplete client state
- the main authentication journeys are covered by autonomous regression tests

Implemented in this sprint:

- Hardened refresh-token behavior so a session can no longer mint a fresh access token after the active tenant membership has been suspended or invalidated
- Fixed the MFA login flow for multi-tenant users so post-verification navigation now returns to the organization picker instead of skipping directly into the app shell
- Added shared frontend auth error mapping for login, invitation acceptance, forgot-password, reset-password, and MFA verification states
- Added autonomous backend and Playwright regression coverage for suspended-access denial, MFA multi-tenant continuation, expired invitations, used reset links, and refresh-token invalidation
- Documented identity recovery expectations for operators in the administrator guide

## Sprint 35 - Operational Reliability, Data Safety, And Migration Discipline

Status: Completed

Goal:
Reduce operational fragility so maintainers can update, validate, and restore the project confidently in a self-hosted open-source context.

Why this sprint now:

- A usable open-source product is not only feature-complete; it must also be recoverable, testable, and predictable during upgrades.
- Current docs and scripts cover important parts of operations, but migration discipline, restore confidence, and operator-safe workflows still need tightening.
- This sprint protects the final two product-facing sprints from being built on shaky operational ground.

Primary dependencies:

- Sprint 23 observability and runtime reliability
- Sprint 24 production validation, recovery, and security hardening
- Sprint 33 and Sprint 34 identity stabilization work

Execution scope:

- migration verification discipline
- backup and restore confidence
- operator-safe maintenance workflows
- docs and scripts aligned with a reproducible self-hosted deployment story

Deliverables:

- Stronger migration validation guidance and any missing guardrails needed for safe schema evolution
- Backup and restore documentation refined for realistic self-hosted usage
- Operational smoke or verification scripts updated where needed to reflect the current stack
- Clear documented expectations for Docker-based validation, health checks, and dependency readiness
- Regression tests or checks added for areas directly touched by operational hardening

Validation requirements:

- relevant backend tests pass
- migration chain remains valid from a fresh database
- operational verification steps are documented and reproducible from the repository

Definition of done:

- maintainers can understand how to upgrade, validate, and recover the product without guesswork
- the project is less dependent on implicit local setup knowledge

Acceptance criteria:

- migration and restore expectations are explicit and current
- no newly introduced operational behavior relies on undocumented manual intervention
- the repo tells a coherent self-hosted deployment story

## Sprint 36 - Association Operations Robustness

Status: Completed

Goal:
Strengthen the most important business workflows so the product is realistically usable by an association or organization with about 200 members.

Why this sprint now:

- Identity and operations hardening should happen before refining association-facing workflows.
- The product already covers members, contributions, events, announcements, policies, and disciplinary records, but the remaining gaps should now be prioritized by real usability and day-to-day administration needs.
- This sprint converts the existing feature base into a more dependable operational tool rather than a feature showcase.

Primary dependencies:

- all previous completed module sprints
- Sprint 35 operational reliability

Execution scope:

- highest-friction business workflow stabilization
- data integrity and operator clarity for association administration
- realistic UX and validation improvements for the most used admin and member paths

Deliverables:

- Focused improvements on the most fragile or incomplete association-management workflows discovered from the current codebase
- Better empty states, validation, error handling, and operator guidance where business actions remain ambiguous
- Additional tenant-isolation and regression coverage for touched membership, contribution, event, announcement, or policy flows
- Documentation updates that clarify what is production-usable now versus what remains intentionally limited

Validation requirements:

- module-specific backend tests pass for every touched business area
- frontend build passes
- browser validation covers the most important association workflows affected by the sprint

Definition of done:

- the project feels coherent and dependable for a small-to-medium organization rather than only technically impressive
- key admin workflows can be demonstrated end to end with fewer ambiguous states and less manual interpretation

Acceptance criteria:

- the sprint addresses the highest-value business friction visible in the real codebase
- touched workflows are validated with realistic tests
- documentation reflects the true practical operating model

## Sprint 37 - Final Open-Source Release Stabilization And Portfolio Readiness

Status: Completed

Goal:
Close the roadmap with a stable, demonstrable, well-documented open-source release candidate suitable for portfolio presentation and real pilot usage.

Why this sprint now:

- The preceding four sprints should leave only final stabilization, verification, and packaging work.
- A strong portfolio-grade open-source project needs a clean handoff story, honest documentation, reproducible validation, and a clearly stated maturity boundary.

Primary dependencies:

- Sprint 33 through Sprint 36

Execution scope:

- final regression sweep
- release-facing documentation cleanup
- open-source usability and handoff quality
- remaining high-value paper cuts that block confident demonstration

Deliverables:

- Final documentation pass across README, status, roadmap, deployment, and handoff files
- Explicit release-positioning notes describing intended usage, scale target, strengths, and known limits
- Final regression test pass summary covering backend, frontend build, and browser checks that matter most
- Cleanup of small but important inconsistencies that would otherwise weaken portfolio presentation
- Clear post-roadmap suggestions for optional future enhancements beyond Sprint 37

Validation requirements:

- relevant automated tests pass
- the application remains buildable and demonstrable
- the documentation matches the verified state of the codebase

Definition of done:

- Kairo is presentable as a stable open-source portfolio project
- the project is realistically usable for a 200-member organization within its documented scope
- another agent or contributor can continue from the repository without hidden context

Acceptance criteria:

- roadmap, status, and handoff documentation all agree on the achieved state
- the release story is honest, polished, and technically defensible
- the project has a clear endpoint for this final five-sprint stabilization track

## Sprint 38 - Treasurer Workspace And Finance Permission Hardening

Status: Completed

Goal:
Turn the seeded `treasurer` role into a real constrained operator by exposing a dedicated finance workspace and aligning backend authorization with the intended role model.

Why this sprint now:

- The roadmap through Sprint 37 delivered an open-source release, but the README still documented a treasurer product gap.
- Backend comments already described mixed `admin` / `treasurer` finance capabilities, yet several endpoints were not explicitly enforcing those rules.
- The product could not honestly claim role maturity while the treasurer persona still landed in a mostly member-only shell.

Deliverables:

- Explicit backend role enforcement on membership and contribution routers
- Admin-only protection for finance export/import/delete operations
- Staff-only protection for member directory lookup, member balance lookup, contribution listing, summary, creation/update, payment recording, and payment history
- Dedicated authenticated frontend route `/finance`
- Sidebar navigation entry for `treasurer` and `admin` users when membership and contributions modules are enabled
- `FinanceWorkspaceView.vue` with:
  - member balance lookup
  - contribution creation
  - payment recording
  - year-scoped contribution summary and ledger table
- Browser regression coverage for the treasurer workspace
- Updated roadmap, status, and README documentation

Acceptance criteria:

- a plain member cannot access staff membership or contribution endpoints
- a treasurer can review member balances and record payments without full admin-console access
- admin-only export and delete operations remain backend-enforced
- the authenticated shell no longer exposes the Admin link because of a template truthiness bug
- frontend build, targeted backend tests, and treasurer browser flow all pass

## Sprint 39 - Role-Aware Dashboard And Action Surface Hardening

Status: Completed

Goal:
Remove the remaining admin-centric guidance shown to non-admin staff users by making dashboard widgets, onboarding actions, and quick links role-aware across the authenticated shell.

Why this sprint next:

- Sprint 38 activated the treasurer workflow, but the current dashboard still presents admin-only actions such as document upload, admin settings, and member import to a treasurer session.
- This is now the clearest remaining role-coherence gap in the product surface.
- Fixing it will improve trust, reduce dead-end navigation, and make the portfolio demo more professionally consistent.

Deliverables:

- Role-aware dashboard quick actions and first-run guidance
- Removal or replacement of admin-only CTA links for treasurer sessions
- Shared capability helpers for frontend role-gated affordances
- Browser coverage for admin vs treasurer dashboard divergence
- Documentation updates for role-specific product walkthroughs

## Sprint 40 - Demo Gallery And Handoff Polish

Status: Completed

Goal:
Refresh the public demo assets and universal handoff materials so the repository tells the same story as the current codebase across screenshots, README, and continuation prompts.

Why this sprint next:

- Sprint 39 made the runtime role surfaces coherent, but the screenshot gallery and public walkthrough text can still drift after UI changes.
- The repository is intended to be resumed by Codex, Cursor, or GitHub Copilot, so the handoff artifacts should be as current as the code itself.
- A final polish sprint is the best place to regenerate screenshots, tighten demo narratives, and align the reusable prompt pack with the actual product surface.

Deliverables:

- Regenerate role-specific screenshots for the public demo gallery
- Update README walkthrough text and image references if needed
- Refresh any continuation or handoff prompts that describe the current sprint model
- Confirm that the treasurer, admin, and member walkthroughs all match the verified UI
- Keep the focus on documentation and demo fidelity rather than new product features

## Professional Association Maturity Track

Estimated additional sprints from the current state: 12

Why 12 sprints are needed:

- The current product base is strong on tenancy, authentication, document RAG, membership, contributions, events, announcements, audit, and operational hardening.
- The main gap is no longer the technical foundation; it is the business-role model and the product surface expected by a real association with multiple office functions.
- Today, most sensitive write flows are still effectively grouped under broad `admin` or `admin/treasurer` checks, which is not enough for roles such as secretary general, censor, auditor, sports manager, president, or vice president.
- The chatbot is already secure for document retrieval, but it is not yet a full role-aware assistant across structured organizational data such as personal balances, finance oversight, sanctions governance, and office workspaces.
- A professional, mature target requires both backend permission refactoring and focused UI workspaces, plus regression coverage for each role. Compressing all of that into fewer sprints would create too much product and security risk.

Current gap summary before this new track:

- Role catalog is still too coarse for the target association model.
- Many write surfaces are still `admin`-only, even where the real business owner should be another office role.
- Members do not yet have a dedicated PDF self-service flow for their own dues and statements.
- There is no dedicated workspace yet for secretary general, censor, sports lead, president, vice president, or principal administrator.
- The chatbot remains document-grounded and does not yet expose carefully filtered structured business answers by role.

## Sprint 41 - Governance Role Matrix And Capability Foundation

Status: Completed

Goal:
Define the professional association role model and introduce a reusable backend capability layer that future sprints can build on safely.

Why this sprint first:

- The target product needs more than `admin`, `member`, and `treasurer`.
- Every later workspace sprint depends on a clean capability matrix.
- If we skip this foundation, later role work will become inconsistent and risky.

Deliverables:

- Canonical tenant role catalog for the association target:
  - `principal_admin`
  - `president`
  - `vice_president`
  - `secretary_general`
  - `treasurer`
  - `auditor`
  - `censor`
  - `sports_manager`
  - `member`
- Capability matrix documenting who can read, write, export, audit, or manage each domain
- Reusable backend helpers for capability checks instead of multiplying inline role checks
- Seed/demo role updates and tenant role catalog refresh
- Audit logging for role assignment and role changes
- Documentation updates for the new target governance model

Acceptance criteria:

- the backend can represent all target office roles without breaking tenant isolation
- role changes remain tenant-scoped and audited
- no existing route becomes less secure during the role-model expansion
- next sprints can depend on named capabilities instead of ad hoc role comparisons

Delivered:

- Canonical association role catalog added under `services/api/app/modules/tenancy/role_catalog.py`
- Reusable capability layer added under `services/api/app/core/capabilities.py`
- `CurrentUser.has_capability()` introduced for backend authorization composition
- Tenant role listing now auto-syncs the canonical role catalog and returns capabilities plus canonical metadata
- Managed-user role replacement endpoint added with audit logging for tenant-scoped role changes
- Invitation acceptance now records explicit audited `role_assigned` events
- Seed data updated to provision the canonical governance role set while preserving legacy `admin` compatibility
- Governance role tests added for catalog exposure, audited role updates, invite acceptance, and compatibility semantics

## Sprint 42 - Fine-Grained Backend Permission Enforcement

Status: Completed

Goal:
Replace broad `admin` and `admin/treasurer` gating with explicit capability enforcement per module and action.

Why this sprint next:

- The current codebase still contains many broad role checks in membership, contributions, documents, policies, events, announcements, and disciplinary flows.
- The professional target requires read/write separation across office roles before new UI spaces are built.

Deliverables:

- Capability-driven backend guards for:
  - member directory read
  - finance read
  - finance write
  - document governance write
  - policy write
  - disciplinary write
  - events write
  - announcements write
  - audit read
  - tenant administration
- Router refactors to consume shared capability checks
- Regression tests for each protected action and each role family
- Updated error messages for denied access

Acceptance criteria:

- ordinary members remain read-only and tenant-safe
- bureau roles receive only their intended write privileges
- auditor access is read-only where required
- principal admin keeps the broadest tenant-scoped access without bypassing tenant isolation

Delivered:

- Shared capability enforcement helper added under `services/api/app/core/authorization.py`
- Membership router refactored onto explicit capabilities for tenant read, finance read, membership write, and tenant administration actions
- Contributions router refactored onto explicit capabilities for finance read, finance write, and tenant administration actions
- Documents router refactored onto explicit document read/write capabilities
- Policies router now uses policy-write capability instead of hardcoded admin checks
- Disciplinary router now uses disciplinary read/write capabilities, removing treasurer's former over-broad mutation access
- Events and announcements routers now use explicit event/announcement write capabilities plus tenant administration for exports
- Audit and admin operational endpoints now use audit-read, document-write, and tenant-administration capabilities
- Added role-family integration coverage for secretary general, sports manager, auditor, censor, principal admin, and negative authorization paths
- Targeted backend authorization suites passed

## Sprint 43 - Member Self-Service And Personal PDF Statements

Status: Completed

Goal:
Give ordinary members a simple, elegant, low-noise workspace centered on their own data and downloadable statements.

Why this sprint next:

- The member experience should stay simple and useful while office roles grow more complex.
- Personal contribution visibility and PDF exports are a core practical need for a real association.

Deliverables:

- Simplified member home focused on:
  - personal profile
  - current balance
  - contribution history
  - announcements and events in read-only mode
- Personal PDF statement export for the authenticated member only
- Optional payment receipt or dues history PDF generation
- Tests proving one member cannot fetch another member's PDF or contribution statement
- UX polish for a sober, professional member surface

Delivered:

- Added authenticated member-only endpoints for:
  - personal contribution history
  - consolidated personal statement data
  - PDF statement download
- Implemented backend PDF generation directly from tenant-scoped member and contribution data
- Refreshed the member self-service view into a cleaner profile, balance, history, and download workspace
- Added integration coverage proving personal statement isolation and PDF content isolation between members
- Verified targeted backend tests and frontend production build

Acceptance criteria:

- a member can view only personal contribution data
- a member can download only personal PDF statements
- the UI is clear, uncluttered, and read-only for ordinary members
- backend enforcement prevents cross-member leakage

## Sprint 44 - Secretary General Workspace And Document Governance

Status: Completed

Goal:
Create the first dedicated office workspace for document governance, statutes, protocols, and announcements.

Why this sprint next:

- The secretary general is one of the clearest non-finance office roles in the target product.
- Kairo already has documents, policies, and announcements; they now need a business-owner workspace instead of generic admin-only handling.

Deliverables:

- `secretary_general` workspace and navigation entry
- Document governance surface for official association content:
  - statutes
  - protocols
  - internal notices
  - meeting-support documents
- Secretary-scoped announcement management
- Secretary-scoped policy/document update permissions where appropriate
- Clear separation between document governance and finance/sanctions/admin powers
- Browser and backend tests for secretary-only write paths

Delivered:

- Added a dedicated `Secretary` workspace layout, overview screen, and navigation entry
- Added secretary-scoped routes for documents, policies, and announcements using the existing capability-enforced backend
- Adapted shared document-management UI so it stays coherent outside the admin console
- Hardened frontend route guards so direct navigation restores session state before evaluating role-restricted workspaces
- Added backend authorization coverage for secretary-negative paths and browser validation for secretary navigation and finance-route denial
- Made Playwright web port selection configurable so browser validation remains reproducible on occupied local ports

Acceptance criteria:

- the secretary general can manage official documents and announcements
- the secretary general cannot access finance mutation or disciplinary administration unless explicitly granted
- document updates remain audited and tenant-scoped

## Sprint 45 - Treasurer And Auditor Finance Console

Status: Completed

Goal:
Mature the finance area into a professional workspace for treasurer operations and auditor oversight.

Why this sprint next:

- Finance is already one of the strongest implemented domains.
- The next maturity step is splitting finance operations from finance oversight.

Deliverables:

- Expanded treasurer workspace for day-to-day dues management
- Read-only auditor (`auditor`) finance cockpit with:
  - association-level totals
  - per-member balances
  - payment history visibility
  - export/report access where appropriate
- Role-specific finance summaries for `principal_admin` and `president`
- Export boundaries for treasurer vs auditor vs member
- Deep backend permission and browser tests for finance visibility and mutation rules

Acceptance criteria:

- the treasurer can manage contributions and payments
- the auditor can inspect finance data without mutating it
- ordinary members cannot access tenant-wide finance reports
- the backend remains the sole enforcement point for finance access

Implementation notes:

- Added tenant-wide payment listing and CSV finance report export endpoints over the existing contributions domain
- Enriched the treasurer workspace with recent payment activity so day-to-day finance work stays in one place
- Added a dedicated read-only auditor workspace with totals, per-member balances, payment history, and export access
- Extended backend authorization tests and browser E2E coverage for treasurer and auditor role boundaries

## Sprint 46 - Censor Discipline Workspace

Status: Planned

Goal:
Create a dedicated disciplinary governance area for the censor role with privacy, traceability, and clear limits.

Why this sprint next:

- Disciplinary data is sensitive and should not remain bundled with broad staff access forever.
- The target product explicitly requires a censor-like role for sanctions and related processes.

Deliverables:

- `censor` role workspace
- Disciplinary management UI aligned to sanction workflows
- Private record visibility rules revisited for censor, principal admin, and affected member
- Audit trail enrichment for sanction creation, update, and closure actions
- Tests for privacy, role isolation, and member self-visibility boundaries

Acceptance criteria:

- the censor can manage disciplinary records inside tenant scope
- ordinary members can only see their own records when policy allows
- treasurer and unrelated office roles cannot browse disciplinary records without explicit permission
- all sanction mutations are audited

## Sprint 47 - Sports Operations Workspace

Status: Planned

Goal:
Introduce a focused workspace for the sports affairs lead to manage sports events without broad administrative power.

Why this sprint next:

- The target association model includes a sports operations owner distinct from generic administration.
- Events already exist; they now need a professional delegated management surface.

Deliverables:

- `sports_manager` role and workspace
- Sports-focused event management views
- Optional event categorization or filtering for sports operations
- Role-specific write access for sports events without document/finance/admin spillover
- Tests for sports-manager write boundaries

Acceptance criteria:

- the sports manager can create and update sports events
- the sports manager cannot manage finance, sanctions, or tenant administration
- members continue to consume events in simple read-only mode

## Sprint 48 - President And Vice President Governance Cockpit

Status: Planned

Goal:
Provide executive workspaces for strategic oversight, cross-module visibility, and limited governance actions.

Why this sprint next:

- The president and vice president need broader organizational visibility than ordinary office roles.
- Their experience should remain focused on oversight, not raw system administration.

Deliverables:

- `president` and `vice_president` dashboards
- Cross-module oversight cards:
  - finance summary
  - key announcements
  - major documents
  - sanctions overview where authorized
  - upcoming events
- Carefully limited governance actions aligned with the capability matrix
- Executive visibility tests proving they do not inherit unrestricted principal-admin powers

Acceptance criteria:

- the president has a coherent cross-module oversight surface
- the vice president has a narrower but still useful executive view
- executive roles do not automatically bypass principal-admin controls

## Sprint 49 - Principal Admin Global Control Plane

Status: Planned

Goal:
Separate true platform-style tenant administration from ordinary office work by formalizing the `principal_admin` role.

Why this sprint next:

- The target product still needs one trusted operator with the broadest tenant-scoped powers.
- That role should be explicit and professionally presented rather than implied by legacy `admin` usage.

Deliverables:

- `principal_admin` role semantics and migration path from legacy `admin`
- Global tenant control plane for:
  - role assignments
  - access review
  - tenant settings
  - high-sensitivity exports
  - module management
  - broad audit access
- Clear UI distinction between office workspaces and principal administration
- Tests proving principal admin has the intended extended access inside tenant scope only

Acceptance criteria:

- the principal admin can access the full tenant control surface
- tenant isolation is still preserved everywhere
- office roles no longer depend on generic `admin` semantics for their day-to-day work

## Sprint 50 - Role-Aware Chat And Structured Knowledge Boundaries

Status: Planned

Goal:
Turn the chatbot into a role-aware assistant that can answer from authorized documents and approved structured data without leaking anything across members or roles.

Why this sprint next:

- This is the highest-value and highest-risk maturity step for the target product.
- The current chatbot is secure for document RAG, but it does not yet cover structured organizational answers by role.

Deliverables:

- Role-aware chat policies per role family
- Structured context adapters for approved domains such as:
  - personal contribution balance
  - finance summaries for authorized roles
  - disciplinary visibility where allowed
  - governance documents
  - events and announcements
- Prompt assembly that clearly separates structured facts from retrieved documents
- Strong regression tests for cross-member and cross-role leakage
- Chat trace updates showing source types and refusal reasons

Acceptance criteria:

- an ordinary member can ask about personal dues but never another member's dues
- an auditor can obtain finance summaries without seeing unrelated private data outside granted scope
- the chatbot remains backend-governed and never self-decides permissions
- refusals are clear whenever evidence is missing or unauthorized

## Sprint 51 - Role-Specific Navigation And UX Simplification

Status: Planned

Goal:
Make the interface feel sober, elegant, and professional for each role by reducing noise and clarifying what matters first.

Why this sprint next:

- After adding the main workspaces, the product must feel simple rather than overloaded.
- The member surface and the office surfaces should not share the same complexity level.

Deliverables:

- Role-specific landing pages and navigation sets
- Reduced sidebar clutter for ordinary members
- Clear workspace entry points for office roles
- Design-system polish for a professional, low-noise visual hierarchy
- Browser QA for each major role surface on desktop and mobile

Acceptance criteria:

- members see a simple, readable interface with fast access to their own essentials
- office roles land in the right workspace without hunting through admin-heavy menus
- the interface remains professional, clear, and not overloaded

## Sprint 52 - Full Regression Matrix And Professional Release Candidate

Status: Planned

Goal:
Close the track with release-level hardening, realistic end-to-end verification, and a clean handoff state.

Why this sprint last:

- All role workspaces, chat boundaries, and exports will need final integrated verification.
- The product target is not just feature completeness; it is maturity and confidence.

Deliverables:

- API and browser regression matrix for all major roles:
  - member
  - secretary general
  - treasurer
  - auditor
  - censor
  - sports manager
  - president
  - vice president
  - principal admin
- Final bug-fix sweep based on regression findings
- Updated demo seed and walkthrough assets for the expanded role model
- Updated README, status, roadmap, and handoff docs
- Release-candidate checklist for a professional association deployment

Acceptance criteria:

- critical role flows pass end-to-end
- no known tenant-isolation or role-leak regression remains open
- documentation is current enough for Codex, Cursor, or Copilot to continue without hidden context
- the repository is ready for a professional release candidate review
