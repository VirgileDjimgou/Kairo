# Project Status

Last updated: 2026-06-28

## Current Sprint

Sprint 9 - Policies, Rules And Discipline

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

## Current Verified Product Surface

- Vue frontend with login, dashboard, app shell, admin shell, admin documents view, admin chat audit view, member profile view, admin members view, admin contributions view, public policies view, member disciplinary view, admin policies view, and admin disciplinary view.
- FastAPI backend with mounted `auth`, `tenants`, `documents`, `admin`, `chat`, `membership`, and `contributions` routers plus `/health`.
- PostgreSQL-backed identity, tenancy, document, version, ingestion-job, chunk, membership, contribution, and payment models.
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
- Fully autonomous backend test suite using SQLite by default, without requiring a local PostgreSQL instance.

## Known Risks

- `allowed_role_ids` naming still reflects the upload/API contract and should be revisited if we want UUID-backed role targeting later.
- OCR for image ingestion is still a placeholder.
- CSV import for member profiles is still a placeholder (noted in sprint deliverables).
- Frontend does not enforce role-based UI restrictions (backend enforces permissions, which is correct by design).
- Dashboard sprint roadmap may display stale data if not updated as sprints progress.
- Frontend tenant switching remains placeholder-driven and not fully API-backed.

## Next Session Rule

Future agent sessions must not continue from memory alone.

They must read:

1. `constitution/KAIRO_CONSTITUTION.md`
2. `IMPLEMENTATION_ROADMAP.md`
3. `PROJECT_STATUS.md`
4. `prompts/CODEX_AUTOPILOT.md`
5. `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

Then they must determine the current sprint and continue only that sprint or the next unfinished sprint.
