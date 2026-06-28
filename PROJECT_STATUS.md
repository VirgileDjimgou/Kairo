# Project Status

Last updated: 2026-06-28

## Current Sprint

Sprint 15 - Commercialization Baseline

Status: Completed

## Source Of Truth

- Constitution: `constitution/KAIRO_CONSTITUTION.md`
- Deep product docs: `orgmind_prompt_pack/`
- Roadmap: `IMPLEMENTATION_ROADMAP.md`
- Autopilot prompt: `prompts/CODEX_AUTOPILOT.md`

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

## Current Verified Product Surface

- Vue frontend with login, dashboard, app shell, admin shell, admin documents view, admin chat audit view, member profile view, admin members view, admin contributions view, public policies view, member disciplinary view, admin policies view, admin disciplinary view, member events view, admin events view, member announcements view, admin announcements view, admin notification extensions view, and admin tenant settings view.
- FastAPI backend with mounted `auth`, `tenants`, `documents`, `admin`, `chat`, `membership`, `contributions`, `events`, `announcements`, and `notifications` routers plus `/health`. Tenants router includes settings endpoints for branding and module toggles.
- PostgreSQL-backed identity, tenancy, document, version, ingestion-job, chunk, membership, contribution, payment, event, and announcement models.
- MinIO-backed object storage provider.
- Redis and Celery ingestion worker flow.
- Parsers for TXT, Markdown, CSV, PDF, DOCX, and WhatsApp exports.
- Ollama embedding provider and Qdrant indexing provider.
- First RAG chat surface with permission-aware retrieval, no-source refusal, citations, and LLM provider abstraction.
- Admin document access controls, admin reindex endpoint, and admin chat query traceability endpoint.
- Membership profiles with CRUD, tenant isolation, and self-view.
- Contribution records with balance calculation and payment recording.
- Public policy browsing and admin policy management.
- Private disciplinary records with role-based staff management.
- Events and announcements with visibility scoping and admin CRUD.
- Optional multi-channel notification foundation with placeholder Email, Telegram, and WhatsApp providers.
- Hardened AI safety: prompt injection defenses in system prompt, untrusted source demarcation,
  access control enforcement before prompt assembly, no-source refusal behavior, citation verification
- Enhanced admin audit view with search, status filter, and summary statistics
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
- MIT License file.
- Enhanced /health endpoint returning available module list.

## Known Risks

- `allowed_role_ids` naming still reflects the upload/API contract and should be revisited if we want UUID-backed role targeting later.
- OCR for image ingestion is still a placeholder.
- CSV import for member profiles is still a placeholder (noted in sprint deliverables).
- Frontend does not enforce role-based UI restrictions (backend enforces permissions, which is correct by design).
- Dashboard sprint roadmap may display stale data if not updated as sprints progress.
- Frontend tenant switching remains placeholder-driven and not fully API-backed.
- Production Docker builds (web production target) have not been tested end-to-end with Docker; the nginx.conf is syntactically correct but needs a real Docker build to confirm.
- Cloudflare Tunnel setup instructions are documented but not yet validated with a real tunnel integration test.
- Backup script is a bash script and may need adaptation for non-Linux hosts (Docker Desktop on Windows/macOS paths).
- Multi-channel providers are placeholders only; no real external gateway integration has been validated yet.
- Module toggles are configurable via the settings API but not yet enforced at the router level — disabling a module does not block its API endpoints.
- Onboarding flow (first-run wizard for new tenants) was scoped out of Sprint 15 as a future enhancement.

## Next Session Rule

Future agent sessions must not continue from memory alone.

They must read:

1. `constitution/KAIRO_CONSTITUTION.md`
2. `IMPLEMENTATION_ROADMAP.md`
3. `PROJECT_STATUS.md`
4. `prompts/CODEX_AUTOPILOT.md`
5. `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

Then they must determine the current sprint and continue only that sprint or the next unfinished sprint.
