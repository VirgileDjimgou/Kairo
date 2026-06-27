# OrgMind AI Architecture

## 1. Architecture Overview

OrgMind AI uses a local-first modular architecture.

```text
Internet User
   ↓
Cloudflare Tunnel
   ↓
Local Reverse Proxy / Web App
   ↓
FastAPI Backend
   ↓
PostgreSQL / Qdrant / MinIO / Redis / Ollama
```

The user runs the backend on a personal machine. Cloudflare Tunnel provides secure external access without requiring public IP configuration or router port forwarding.

---

## 2. Container Architecture

```text
orgmind-ai/
  apps/web                Vue 3 + TypeScript + Pinia + Bootstrap
  services/api            FastAPI backend
  services/worker         Background ingestion worker
  infra/docker            Docker Compose and service configs
  infra/cloudflare        Tunnel configuration examples
  infra/postgres          init scripts and migrations notes
  infra/qdrant            vector DB notes
  infra/minio             object storage notes
  docs                    architecture, prompts, sprints, ADRs
  seed                    demo tenants and sample data
```

Runtime containers:

```text
web        -> frontend static app or Vite dev server
api        -> FastAPI REST API
worker     -> ingestion/background worker
postgres   -> relational database
qdrant     -> vector database
minio      -> object storage
redis      -> queue/cache
ollama     -> local LLM runtime
cloudflared -> optional tunnel sidecar
```

---

## 3. Logical Architecture

```text
Frontend Layer
  - Vue views
  - Pinia stores
  - typed API client
  - route guards

API Layer
  - FastAPI routers
  - DTOs
  - auth dependencies
  - tenant resolver

Application Layer
  - use cases
  - permission checks
  - orchestration

Domain Layer
  - entities
  - value objects
  - policies
  - access rules

Infrastructure Layer
  - PostgreSQL repositories
  - Qdrant adapter
  - MinIO adapter
  - Ollama adapter
  - OCR/parser adapters
```

---

## 4. Backend Module Layout

```text
services/api/app/
  main.py
  core/
    config.py
    security.py
    logging.py
    dependencies.py
  modules/
    identity/
      router.py
      models.py
      schemas.py
      service.py
      repository.py
    tenancy/
    documents/
    ingestion/
    rag/
    chat/
    membership/
    contributions/
    events/
    policies/
    audit/
    admin/
  providers/
    llm/
    embeddings/
    vector_store/
    object_storage/
    parsers/
    ocr/
  db/
    session.py
    base.py
    migrations/
  tests/
```

---

## 5. Frontend Module Layout

```text
apps/web/src/
  main.ts
  App.vue
  router/
    index.ts
    guards.ts
  stores/
    auth.store.ts
    tenant.store.ts
    chat.store.ts
    documents.store.ts
    admin.store.ts
  api/
    http.ts
    auth.api.ts
    documents.api.ts
    chat.api.ts
    admin.api.ts
  layouts/
    AuthLayout.vue
    AppLayout.vue
    AdminLayout.vue
  views/
    auth/
    dashboard/
    chat/
    documents/
    admin/
    contributions/
    events/
    policies/
    audit/
  components/
    common/
    chat/
    documents/
    admin/
  styles/
    main.scss
    variables.scss
```

---

## 6. Data Architecture

### PostgreSQL
Stores:

- tenants
- users
- roles
- permissions
- documents
- ingestion jobs
- conversations
- messages
- structured business records
- audit logs

### MinIO
Stores:

- original uploaded files
- OCR artifacts if needed
- generated exports

### Qdrant
Stores:

- document chunks
- vector embeddings
- metadata payloads for filtering

### Redis
Stores:

- background jobs
- temporary cache
- rate limiting later

### Ollama
Runs:

- local LLM
- optionally local embedding model

---

## 7. RAG Flow

```text
User asks question
   ↓
API authenticates user
   ↓
API resolves tenant and permissions
   ↓
API builds access filter
   ↓
Qdrant retrieves only authorized chunks
   ↓
Backend builds protected prompt
   ↓
LLM generates answer
   ↓
Backend validates citations
   ↓
Answer stored and returned
```

Access filtering happens before retrieval and before LLM context assembly.

---

## 8. Document Ingestion Flow

```text
Admin uploads file
   ↓
API stores original in MinIO
   ↓
API creates document metadata in PostgreSQL
   ↓
Worker receives ingestion job
   ↓
Parser extracts text
   ↓
OCR runs if needed
   ↓
Chunker creates chunks
   ↓
Embedding provider computes vectors
   ↓
Qdrant stores vectors with metadata
   ↓
Job status becomes completed or failed
```

---

## 9. Cloudflare Tunnel Deployment

```text
Public URL
   ↓
Cloudflare Edge
   ↓
cloudflared tunnel
   ↓
localhost reverse proxy
   ↓
web/api containers
```

Recommended routing:

- `https://orgmind.example.com` -> frontend
- `https://orgmind.example.com/api` -> backend API

Alternative:

- `https://app.example.com` -> frontend
- `https://api.example.com` -> backend

---

## 10. Security Architecture

Security controls:

- JWT authentication
- password hashing
- RBAC
- tenant isolation
- document access scopes
- file validation
- audit logs
- CORS restriction
- secure cookies optional later
- Cloudflare Access optional later
- backup encryption recommended

LLM-specific controls:

- retrieval filters before prompt assembly
- retrieved text treated as untrusted
- system prompts separated from documents
- source-based answer requirement
- answer refusal if no evidence

---

## 11. Scaling Path

Stage 1:

```text
Single machine, Docker Compose, local LLM
```

Stage 2:

```text
Personal machine for API, remote LLM optional
```

Stage 3:

```text
VPS deployment, managed domain, automated backups
```

Stage 4:

```text
SaaS mode, separate tenants, monitoring, billing, managed database
```

---

## 12. Architectural Decision

Use a modular monolith for the backend initially.

Reason:

- simpler deployment
- easier local hosting
- fewer moving parts
- better for solo development
- easier for Codex/Copilot to reason about

Extract services only when a module has independent scaling or lifecycle needs.
