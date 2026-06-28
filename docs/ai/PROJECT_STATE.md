# Project State

Last verified against repository code on 2026-06-28.

## Product Snapshot

Kairo, also positioned as OrgMind AI, is a local-first multi-tenant RAG platform for organizations.

Current implementation already includes:

- Vue 3 frontend shell with auth flow, dashboard, admin console, and full CRUD views
- FastAPI backend with identity, tenancy, documents, ingestion, indexing, chat, membership, contributions, policies, disciplinary, events, and announcements modules
- PostgreSQL for relational data
- MinIO for uploaded files
- Redis and Celery for ingestion jobs
- Ollama embeddings + LLM providers
- Qdrant vector indexing with permission-aware retrieval
- CORS middleware, JWT auth, RBAC, tenant isolation
- Production deployment infrastructure
- Hardened AI safety with prompt injection defenses and source demarcation
- Enhanced audit review screen
- Optional notification extension foundation with Email, Telegram, and WhatsApp placeholders

## Implemented Sprints

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

## Not Yet Implemented

- Sprint 15: Commercialization Baseline

## Known Gaps And Risks

- OCR for image ingestion is still a placeholder.
- CSV import for member profiles is still a placeholder.
- Frontend tenant switcher is still placeholder-driven and not API-backed.
- Frontend does not enforce role-based UI restrictions (backend enforces permissions, which is correct by design).
- Production Docker builds not yet validated end-to-end.
- Multi-channel providers are still simulated placeholders and not connected to external gateways.

## Rules For Future Sessions

- Preserve the existing module pattern under `services/api/app/modules/`.
- Do not jump to later roadmap modules before the active sprint is complete.
- When sprint progress changes, update this file and `docs/ai/NEXT_SPRINT.md`.
