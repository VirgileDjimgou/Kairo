# Kairo — OrgMind AI

A **local-first, multi-tenant RAG platform** for associations, clubs, NGOs, and small businesses.

Upload internal documents, manage members and permissions, and run a private AI assistant that answers questions with source citations — entirely on your own hardware.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Vue 3)                   │
│     apps/web/ — Vite · Pinia · Bootstrap 5           │
│     Login · Dashboard · Admin · Member views         │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP (REST API)
┌──────────────────▼──────────────────────────────────┐
│              Backend (FastAPI / Python)              │
│     services/api/ — Modular monolith                 │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │
│  │  Auth &  │ │ Document │ │   Membership &     │   │
│  │ Tenancy  │ │   Mgmt   │ │  Contributions     │   │
│  └──────────┘ └──────────┘ └────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │
│  │ Policies │ │  Events  │ │Chat / RAG + Vector │   │
│  │ & Disc.  │ │ & Ann.   │ │ Search & Retrieval │   │
│  └──────────┘ └──────────┘ └────────────────────┘   │
│                                                      │
│  Provider pattern: LLM · Embeddings · Vector Store   │
└───┬──────┬──────┬──────┬──────┬──────┬──────────────┘
    │      │      │      │      │      │
    ▼      ▼      ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────────────┐
│ PG │ │Redis│ │MinIO│ │Qdrant│ │Celery│ │ Ollama     │
└────┘ └────┘ └────┘ └────┘ └────┘ └────────────┘
  DB    Queue   Storage  Vector  Worker  Local LLM
```

**Key design decisions:**
- **Backend enforces all permissions** — the LLM never decides access control
- **Tenant isolation** on every DB query (every request carries `tenant_id`)
- **RAG retrieval** is filtered by tenant and access scope before the LLM sees anything
- **Provider pattern** — all infrastructure behind interfaces (swap Ollama → OpenAI, Qdrant → Pinecone, etc.)
- **Autonomous tests** default to SQLite — portable on any machine or agentic IDE

## Quick Start

```bash
# 1. Prerequisites
#    - Docker & Docker Compose
#    - Git
#    - ~8 GB free RAM (for Ollama + Qdrant + services)

# 2. Clone and enter the repo
git clone <repo-url> kairo
cd kairo

# 3. Copy environment config
cp .env.example .env

# 4. Start all services (first pull may take a few minutes)
docker compose up --build

# 5. In another terminal, seed demo data
docker compose exec api python -m app.db.seed

# 6. Access the app
#    Frontend:  http://localhost:5173
#    API docs:  http://localhost:8000/docs
```

### Demo Credentials

| Role       | Email                 | Password       |
| ---------- | --------------------- | -------------- |
| Admin      | admin@demo.org        | Admin123!      |
| Member     | alice@demo.org        | Member123!     |
| Member     | bob@demo.org          | Member123!     |
| Treasurer  | treasurer@demo.org    | Treasurer123!  |

## Project Structure

```
kairo/
├── apps/web/            Vue 3 frontend (TypeScript, Pinia, Bootstrap 5)
├── services/api/        FastAPI backend (modular monolith)
│   ├── app/
│   │   ├── modules/     Domain modules (tenancy, identity, documents, chat,
│   │   │                membership, contributions, policies, disciplinary,
│   │   │                events, announcements)
│   │   ├── db/          Session, migrations, seed scripts
│   │   └── core/        Security, logging, provider abstractions
│   └── tests/           82+ integration tests (SQLite, no infra needed)
├── infra/               Infrastructure config samples (nginx, caddy, cloudflare)
├── docs/                Architecture docs, ADRs, sprint notes, deployment guide
├── orgmind_prompt_pack/ Source-of-truth product documentation
├── scripts/             Utility scripts (backup, etc.)
├── seed/                Demo tenant data helpers
├── constitution/        Project constitution and rules
└── prompts/             AI agent startup prompts (Codex, Cursor, Copilot)
```

## Demo Walkthrough

See [`docs/demo-script.md`](docs/demo-script.md) for a complete walkthrough covering:

1. **Admin login** — browse members, manage documents, view policies, configure tenant settings & module toggles
2. **Member login** — view profile, check balance, see events and announcements
3. **RAG chat** — ask questions about bylaws and policies with cited answers
4. **AI safety** — prompt injection resistance, no-source refusal
5. **Treasurer view** — manage contributions and payments

## Commercial Packaging

If you want to present Kairo as a product rather than only a codebase, start here:

1. [`docs/commercial/README.md`](docs/commercial/README.md) - commercial overview and reading order
2. [`docs/commercial/public-entry.md`](docs/commercial/public-entry.md) - what the public login surface communicates
3. [`docs/commercial/onboarding-guide.md`](docs/commercial/onboarding-guide.md) - customer onboarding flow
4. [`docs/commercial/administrator-guide.md`](docs/commercial/administrator-guide.md) - tenant admin operations
5. [`docs/commercial/support-playbook.md`](docs/commercial/support-playbook.md) - support boundary and incident workflow
6. [`docs/commercial/feature-matrix.md`](docs/commercial/feature-matrix.md) - included modules and future boundaries
7. [`docs/commercial/commercialization-notes.md`](docs/commercial/commercialization-notes.md) - service-led offer structure
8. [`docs/commercial/demo-to-production-checklist.md`](docs/commercial/demo-to-production-checklist.md) - go-live transition checklist
9. [`docs/commercial/maturity-review.md`](docs/commercial/maturity-review.md) - remaining legal and business decisions

## Development

```bash
# API tests (SQLite by default — no local PostgreSQL needed)
cd services/api
pip install -r requirements.txt
pytest

# Frontend dev server
cd apps/web
npm install
npm run dev

# With Cloudflare Tunnel (expose to internet)
docker compose --profile tunnel up --build
```

For production deployment with nginx, Cloudflare Tunnel, and backups, see [`docs/deployment-guide.md`](docs/deployment-guide.md).

## Multi-IDE Workflow

This repository can be continued from Codex, Cursor, or GitHub Copilot without losing sprint context.

Read these files at the start of every new AI-assisted session:

1. `constitution/KAIRO_CONSTITUTION.md`
2. `IMPLEMENTATION_ROADMAP.md`
3. `PROJECT_STATUS.md`
4. `prompts/CODEX_AUTOPILOT.md`

Reusable prompts: `prompts/CODEX_AUTOPILOT.md` · `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

## License

MIT
