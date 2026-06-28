# Project Status

Last updated: 2026-06-28

## Current Sprint

Sprint 8 - Membership And Contributions

Status: Ready to start

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

## Current Verified Product Surface

- Vue frontend with login, dashboard, app shell, admin shell, admin documents view, and admin chat audit view.
- FastAPI backend with mounted `auth`, `tenants`, and `documents` routers plus `/health`.
- PostgreSQL-backed identity, tenancy, document, version, ingestion-job, and chunk models.
- MinIO-backed object storage provider.
- Redis and Celery ingestion worker flow.
- Parsers for TXT, Markdown, CSV, PDF, DOCX, and WhatsApp exports.
- Ollama embedding provider and Qdrant indexing provider.
- First RAG chat surface with permission-aware retrieval, no-source refusal, citations, and LLM provider abstraction.
- Admin document access controls, admin reindex endpoint, and admin chat query traceability endpoint.
- Fully autonomous backend test suite using SQLite by default, without requiring a local PostgreSQL instance.

## Known Risks

- `allowed_role_ids` naming still reflects the upload/API contract and should be revisited if we want UUID-backed role targeting later.
- Frontend tenant switching is still placeholder-driven and not fully API-backed.
- OCR for image ingestion is still a placeholder.
- Sprint 8 needs a clear data model and UI slice for structured membership and contribution records.

## Next Session Rule

Future agent sessions must not continue from memory alone.

They must read:

1. `constitution/KAIRO_CONSTITUTION.md`
2. `IMPLEMENTATION_ROADMAP.md`
3. `PROJECT_STATUS.md`
4. `prompts/CODEX_AUTOPILOT.md`

Then they must determine the current sprint and continue only that sprint or the next unfinished sprint.
