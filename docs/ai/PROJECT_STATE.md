# Project State

Last verified against repository code on 2026-06-29.

## Product Snapshot

Kairo, also positioned as OrgMind AI, is a local-first multi-tenant RAG platform for organizations.

Current implementation already includes:

- Vue 3 frontend shell with auth flow (multi-tenant), dashboard, admin console, full CRUD views
- FastAPI backend with identity, tenancy, documents, ingestion, indexing, chat, membership, contributions, policies, disciplinary, events, and announcements modules
- PostgreSQL for relational data
- MinIO for uploaded files
- Redis and Celery for ingestion jobs
- Ollama embeddings + LLM providers
- Qdrant vector indexing with permission-aware retrieval
- Document operations with OCR for images, bulk upload, archive/unarchive, and ingestion retry
- Runtime observability with `/health`, `/metrics`, request IDs, and ingestion job health visibility
- CORS middleware, JWT auth, RBAC, tenant isolation
- Production deployment infrastructure
- Hardened AI safety with prompt injection defenses and source demarcation
- Enhanced audit review screen
- Optional notification extension foundation with Email, Telegram, and WhatsApp placeholders
- Tenant settings API with branding and module toggles
- API-driven multi-tenant UX with tenant switching and module-aware navigation
- Audit trail API and admin review screen for sensitive actions
- Public product landing surface on the login page with trust signals and a clear sign-in path
- Guided tenant onboarding dashboard with checklist-driven first-run orientation
- Admin operations hub with module-aware metrics, watchlist, and quick actions
- Admin access operations console with tenant role selection, invitation visibility, and cancellation controls
- Authenticated account security surface with MFA status, self-service MFA management, and password recovery launch
- SMTP-backed identity message delivery for invitations and password recovery, with delivery-state visibility and safe production token hiding
- Persistent session governance for authenticated users, including active-session inventory, revoke controls, and recent security-event visibility
- Tenant user lifecycle governance for administrators, including suspension, reactivation, tenant-scoped session containment, and backend membership revalidation
- Authentication recovery hardening with clearer denial states, MFA multi-tenant continuation, and stricter refresh-token session validation

## ## Implemented Sprints

- Sprint 0: Foundation and repository skeleton
- Sprint 1: Identity, tenancy, and JWT auth
- Sprint 2: Professional Vue layout
- Sprint 3: Document upload and object storage
- Sprint 4: Ingestion worker and parsing
- Sprint 5: Embeddings and Qdrant indexing
- Sprint 6: First RAG chat
- Sprint 7: Admin RAG controls
- Sprint 8: Membership and contributions
- Sprint 9: Policies, rules, and discipline
- Sprint 10: Events and announcements
- Sprint 11: Cloudflare Tunnel Deployment
- Sprint 12: Evaluation and AI Safety
- Sprint 13: Demo Tenant and Portfolio Polish
- Sprint 14: Multi-Channel Extensions
- Sprint 15: Commercialization Baseline
- Sprint 16: Tenant Activation And Multi-Tenant UX
- Sprint 17: Identity Lifecycle And Access Hardening
- Sprint 18: Module Enforcement And Entitlements
- Sprint 19: Audit Trail And Administrative Governance
- Sprint 20: Document Operations Maturity
- Sprint 21: Data Import And Backoffice Automation
- Sprint 22: Product UX Polish And Browser QA
- Sprint 23: Observability And Runtime Reliability
- Sprint 24: Production Validation, Recovery And Security Hardening
- Sprint 25: Commercial Packaging And Launch Readiness
- Sprint 26: Public Product Landing And Lead Capture
- Sprint 27: Guided Tenant Onboarding And Conversion Flow
- Sprint 28: Admin Overview And Tenant Operations Hub
- Sprint 29: Team Invitations And Access Operations Console
- Sprint 30: Account Security And Identity Self-Service
- Sprint 31: Secure Identity Message Delivery And Access Notifications
- Sprint 32: Session Governance And Security Event Operations
- Sprint 33: Tenant User Lifecycle Governance And Account Lockdown
- Sprint 34: Authentication Hardening And Recovery Stability
- Sprint 35: Operational Reliability, Data Safety, And Migration Discipline

## Remaining Roadmap

The product now enters its final five-sprint open-source stabilization track.

Target frame:

- stable, portfolio-grade open-source release
- usable by an association or organization of about 200 members
- finish within Sprint 35 through Sprint 37

Immediate next sprint:

- Sprint 36 - Association Operations Robustness

## Known Gaps And Risks

- Production Docker builds were validated end-to-end, but `/health` still reports `ollama` as unavailable when the model container is not running.
- Only email is wired for real identity delivery; multi-channel providers beyond email remain simulated placeholders.
- The roadmap now prioritizes stability and practical usability over additional commercial-positioning work.
- A deeper first-run wizard remains a future enhancement beyond the current guided checklist.
- Playwright coverage for login and dashboard is autonomous, but broader admin/business E2E still benefits from a live API stack.
- Sprint 24 has been completed with a validated production build and smoke run.
- Sprint 25 has been completed with the commercial packaging documentation set.
- Sprint 26 has been completed with the public entry commercial surface.
- Sprint 27 has been completed with guided onboarding for new tenant admins.
- Sprint 28 has been completed with a real admin operations hub.
- Sprint 29 has been completed with in-product invitation operations.
- Sprint 30 has been completed with self-service account security UX.
- Sprint 31 has been completed with secure outbound identity delivery and delivery-state visibility.
- Sprint 32 has been completed with session governance and current-user security event operations.
- Sprint 33 has been completed with tenant user lifecycle governance and account lockdown.
- Sprint 34 has been completed with authentication hardening and recovery stability.
- Sprint 35 has been completed with operational reliability, migration gap fixes, restore automation, and Docker healthchecks.
- Sprint 36 through Sprint 37 now remain in the final planned stabilization track for the current open-source target.

## Rules For Future Sessions

- Preserve the existing module pattern under `services/api/app/modules/`.
- Do not jump to later roadmap modules before the active sprint is complete.
- When sprint progress changes, update this file and `docs/ai/NEXT_SPRINT.md`.
