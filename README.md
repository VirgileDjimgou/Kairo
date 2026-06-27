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
# API tests (requires PostgreSQL running)
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

## Architecture

- **Backend** enforces all permissions — the LLM never decides access control
- **Tenant isolation** is mandatory on every DB query
- **RAG retrieval** is filtered by `tenant_id` and access scope before the LLM sees anything
- **Provider pattern** — all infrastructure (LLM, embeddings, vector store, storage) is behind interfaces

See `orgmind_prompt_pack/` for full architecture documentation.

## License

MIT
