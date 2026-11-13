# GitHub Copilot Instructions — Kairo (OrgMind AI)

This is a local-first, multi-tenant RAG platform for organizations.

## Source of truth

Start from the session brief, then read only what the task needs:

- `docs/ai/SESSION_BRIEF.md` (generated; or run `npm run session:brief`)
- `AGENTS.md`
- `constitution/KAIRO_CONSTITUTION.md` when the change touches policy or authorization

Do not read `IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md` or
`orgmind_prompt_pack/` in full to get oriented. They are historical reference;
grep the section a task names.

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

- Determine the current sprint from `docs/roadmap/KAIRO_V2_ROADMAP.json` plus the
  batch state machine; `npm run session:brief` prints both.
- Never infer sprint progress from `PROJECT_STATUS.md` or `IMPLEMENTATION_ROADMAP.md`
  prose, and do not skip ahead unless explicitly requested.
- Record sprint transitions through `scripts/sprint-batch/cli.mjs`; update
  `PROJECT_STATUS.md` when the delivered product state changes.

## Flutter client (FROZEN / LEGACY REFERENCE)

- The Vue 3 PWA under `apps/web/` is the canonical client. Flutter
  (`apps/flutter_kairo/`) is frozen as legacy/reference code (ADR-014): no new
  business features, not a blocking job of the default release pipeline, and no
  replacement of the PWA.
- For reference inspection only, read `apps/flutter_kairo/AGENTS.md`,
  `docs/pwa/FLUTTER_TO_PWA_PARITY.md`, `docs/flutter/PROJECT_STATUS.md`,
  `docs/flutter/FLUTTER_APP_ROADMAP.md`, and `docs/flutter/FEATURE_PARITY.md`.
- Treat FastAPI as the only source of authorization and business truth. Neither
  client may validate finance, discipline, role, or tenant permissions by itself.
- Flutter source is preserved for behavior, notification and parity reference;
  archival or deletion is a separate explicit decision after S128.
