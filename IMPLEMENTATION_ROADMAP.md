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

Status: Planned

Goal:
Document and harden local-first remote exposure for demo and small production-like setups.

## Sprint 12 - Evaluation And AI Safety

Status: Planned

Goal:
Add prompt-injection tests, no-source answer rules, and retrieval safety verification.

## Sprint 13 - Demo Tenant And Portfolio Polish

Status: Planned

Goal:
Prepare a recruiter-friendly and client-friendly local demo.

## Sprint 14 - Multi-Channel Extensions

Status: Planned

Goal:
Add optional messaging and notification provider extensions without polluting the core product.

## Sprint 15 - Commercialization Baseline

Status: Planned

Goal:
Prepare onboarding, settings, observability, backup posture, and product readiness foundations.
