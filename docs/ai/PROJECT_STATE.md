# Project State

Last verified against repository code on 2026-06-28.

## Product Snapshot

Kairo, also positioned as OrgMind AI, is a local-first multi-tenant RAG platform for organizations.

Current implementation already includes:

- Vue 3 frontend shell with auth flow and admin documents screen
- FastAPI backend with identity, tenancy, documents, ingestion, and indexing modules
- PostgreSQL for relational data
- MinIO for uploaded files
- Redis and Celery for ingestion jobs
- Ollama embeddings provider
- Qdrant vector indexing

## Implemented Sprints

- Sprint 0: Foundation and repository skeleton
- Sprint 1: Identity, tenancy, and JWT auth
- Sprint 2: Professional Vue layout
- Sprint 3: Document upload and object storage
- Sprint 4: Ingestion worker and parsing
- Sprint 5: Embeddings and Qdrant indexing

## Not Yet Implemented

- Sprint 6: First RAG chat
- Sprint 7: Admin RAG controls
- Sprint 8: Membership and contributions
- Sprint 9: Policies, rules, and discipline
- Sprint 10: Events and announcements
- Sprint 11+: deployment hardening, evaluation, portfolio polish, integrations, commercialization

## Current Backend Surface

Mounted API routers:

- `/api/v1/auth/*`
- `/api/v1/tenants/*`
- `/api/v1/documents/*`
- `/health`

There is no chat or RAG query endpoint yet.

## Known Gaps And Risks

- No `rag` or `chat` module yet.
- Frontend tenant switcher is still placeholder data and not API-driven.
- `allowed_role_ids` is accepted during upload but is not yet enforced through stored metadata and retrieval filters.
- Document lifecycle status likely needs cleanup after successful ingestion.
- Some schema details should be aligned between ORM models and migrations.
- OCR is still a placeholder; image uploads are accepted but fail ingestion intentionally until OCR is implemented.

## Rules For Future Sessions

- Preserve the existing module pattern under `services/api/app/modules/`.
- Do not jump to later roadmap modules before the active sprint is complete.
- When sprint progress changes, update this file and `docs/ai/NEXT_SPRINT.md`.
