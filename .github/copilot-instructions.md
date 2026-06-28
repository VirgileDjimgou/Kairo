# GitHub Copilot Instructions — Kairo (OrgMind AI)

This is a local-first, multi-tenant RAG platform for organizations.

## Source of truth

Read these files before making changes:

- `AGENTS.md`
- `constitution/KAIRO_CONSTITUTION.md`
- `IMPLEMENTATION_ROADMAP.md`
- `PROJECT_STATUS.md`
- `orgmind_prompt_pack/00_MASTER_PROMPT_CODEX.md`
- `orgmind_prompt_pack/01_PROJECT_CONSTITUTION.md`
- `orgmind_prompt_pack/02_ARCHITECTURE.md`
- `orgmind_prompt_pack/03_ROADMAP_SPRINTS.md`

## Hard rules

- Never hardcode COMBIS as product logic — COMBIS is a demo tenant only
- `tenant_id` is mandatory in every tenant-scoped DB query
- Backend enforces all permissions — the LLM never decides access control
- Qdrant retrieval filters must run before prompt assembly
- Never send unauthorized chunks to the LLM
- Frontend never talks directly to PostgreSQL, Qdrant, MinIO, Redis, or Ollama
- Use DTOs at all API boundaries — never expose SQLAlchemy models
- Update tests and docs when behavior changes
- Keep UI elegant, Bootstrap 5-based, and professional

## Security rules

- Use `PyJWT` (not `python-jose`) — avoid algorithm-confusion CVEs
- Use `psycopg[async]` with `postgresql+psycopg://` DSN — async SQLAlchemy
- Always scope repository methods with `tenant_id`
- Validate file uploads: extension allowlist + MIME type + size limit
- Audit log all sensitive admin actions

## Stack

- FastAPI · SQLAlchemy 2.x async · Alembic · PostgreSQL
- Vue 3 · TypeScript · Pinia · Bootstrap 5
- Qdrant · MinIO · Redis · Ollama
- Docker Compose · Cloudflare Tunnel

## Module pattern

Each module under `services/api/app/modules/` contains:
`models.py` · `schemas.py` · `repository.py` · `service.py` · `router.py`

Repository methods always accept `tenant_id: UUID` as a mandatory argument.

## Sprint continuity

- Determine the current sprint from `PROJECT_STATUS.md` and `IMPLEMENTATION_ROADMAP.md`.
- Do not skip ahead to later roadmap sprints unless explicitly requested.
- If sprint progress changes, update `PROJECT_STATUS.md` and `IMPLEMENTATION_ROADMAP.md`.
