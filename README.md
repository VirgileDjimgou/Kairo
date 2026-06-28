# Kairo — OrgMind AI

A **local-first, multi-tenant RAG platform** for associations, clubs, NGOs, and small businesses.

Kairo lets organizations upload internal documents, manage members and permissions, and run a private AI assistant that answers questions with source citations — entirely on your own hardware.

## Stack

| Layer          | Technology                                             |
| -------------- | ------------------------------------------------------ |
| Frontend       | Vue 3 · TypeScript · Pinia · Bootstrap 5 · Vite        |
| Backend        | Python 3.12 · FastAPI · SQLAlchemy 2.x async · Alembic |
| Database       | PostgreSQL 16                                          |
| Vector DB      | Qdrant                                                 |
| Object Storage | MinIO                                                  |
| Queue          | Redis + Celery                                         |
| Local LLM      | Ollama (`qwen2.5:7b-instruct`)                         |
| Runtime        | Docker Compose                                         |
| Remote Access  | Cloudflare Tunnel                                      |

## Quick Start

```bash
# 1. Copy environment config
cp .env.example .env

# 2. Start all services
docker compose up --build

# 3. Seed demo tenant and admin user
docker compose exec api python -m app.db.seed

# 4. Access the app
#    Frontend:  http://localhost:5173
#    API:       http://localhost:8000
#    API docs:  http://localhost:8000/docs
#
#    Demo login: admin@demo.org / Admin123!
```

## Project Structure

```
apps/web/          Vue 3 frontend (TypeScript, Pinia, Bootstrap 5)
services/api/      FastAPI backend (modular monolith)
infra/             Infrastructure configuration samples
docs/              Architecture docs, ADRs, sprint notes
seed/              Demo tenant data (anonymized)
orgmind_prompt_pack/  Source-of-truth product documentation
```

## Development

```bash
# API tests (runs on SQLite by default, no local PostgreSQL required)
cd services/api
pip install -r requirements.txt
pytest

# Frontend dev server
cd apps/web
npm install
npm run dev

# With Cloudflare Tunnel
docker compose --profile tunnel up --build
```

## Multi-IDE Workflow

This repository can be continued from Codex, Cursor, or GitHub Copilot without losing sprint context.

Read these files at the start of every new AI-assisted session:

1. `constitution/KAIRO_CONSTITUTION.md`
2. `IMPLEMENTATION_ROADMAP.md`
3. `PROJECT_STATUS.md`
4. `prompts/CODEX_AUTOPILOT.md`

Reusable prompts are available here:

- `prompts/CODEX_AUTOPILOT.md`
- `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

## Architecture

- **Backend** enforces all permissions — the LLM never decides access control
- **Tenant isolation** is mandatory on every DB query
- **RAG retrieval** is filtered by `tenant_id` and access scope before the LLM sees anything
- **Provider pattern** — all infrastructure (LLM, embeddings, vector store, storage) is behind interfaces
- **Autonomous tests** default to SQLite, which makes the suite portable on any machine or agentic IDE
- **Admin traceability** includes document access control, reindexing, and chat query audit views

See `orgmind_prompt_pack/` for full architecture documentation.

## License

MIT
