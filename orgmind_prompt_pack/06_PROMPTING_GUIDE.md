# Prompting Guide for Codex and GitHub Copilot

This guide defines how to ask AI coding tools to implement OrgMind AI safely and progressively.

---

## 1. General Prompt Pattern

Use this structure for every implementation request:

```text
You are working on OrgMind AI.
Read these files first:
- 00_MASTER_PROMPT_CODEX.md
- 01_PROJECT_CONSTITUTION.md
- 02_ARCHITECTURE.md
- 03_ROADMAP_SPRINTS.md

Implement: [specific feature]

Target module: [module]
Expected files: [list]
Rules:
- preserve tenant isolation
- enforce permissions in backend
- do not modify unrelated modules
- add or update tests
- update documentation if needed
- keep the implementation small and explicit

Acceptance criteria:
- [criterion 1]
- [criterion 2]
- [criterion 3]
```

---

## 2. Anti-patterns

Do not prompt like this:

```text
Build the whole app.
Make everything work.
Add AI everywhere.
Create the full RAG system.
Fix the architecture.
```

Use small prompts instead:

```text
Implement the Tenant SQLAlchemy model and Alembic migration.
Implement the document upload endpoint with MinIO storage.
Implement permission-aware Qdrant retrieval for chat queries.
Implement the Vue document upload page.
```

---

## 3. Sprint 0 Prompt

```text
You are implementing Sprint 0 for OrgMind AI.

Read:
- 00_MASTER_PROMPT_CODEX.md
- 01_PROJECT_CONSTITUTION.md
- 02_ARCHITECTURE.md
- 03_ROADMAP_SPRINTS.md

Create the initial monorepo structure.

Expected output:
- apps/web Vue 3 + TypeScript + Vite skeleton
- services/api FastAPI skeleton
- docs folders
- infra folders
- docker-compose.yml
- .env.example
- README.md
- /health endpoint

Rules:
- do not implement auth yet
- do not implement RAG yet
- keep placeholders explicit
- use English for code and file names
- make Docker Compose ready for future services

Acceptance criteria:
- frontend starts
- API starts
- /health returns ok
- README explains how to run the project
```

---

## 4. Sprint 1 Prompt

```text
Implement Sprint 1: Identity, Tenancy and Auth.

Target backend module:
- services/api/app/modules/identity
- services/api/app/modules/tenancy

Expected files:
- SQLAlchemy models for Tenant, User, Role, Permission, TenantUser
- Pydantic schemas
- auth router
- JWT service
- password hashing service
- tenant dependency
- tests for login and tenant scoping

Rules:
- every user belongs to tenants through TenantUser
- no endpoint should return data across tenants
- do not implement document upload yet
- use Alembic migration

Acceptance criteria:
- admin user can login
- token contains user id and active tenant id
- protected endpoint works
- tests pass
```

---

## 5. Sprint 3 Prompt: Document Upload

```text
Implement document upload for OrgMind AI.

Target modules:
- documents
- providers/object_storage

Expected files:
- Document model
- DocumentVersion model
- DocumentAccessScope enum
- MinIOObjectStorageProvider
- upload endpoint
- list documents endpoint
- tests

Rules:
- only authenticated tenant users can upload
- uploaded documents must be tenant-scoped
- store original files in MinIO
- store metadata in PostgreSQL
- do not run ingestion yet, only create an ingestion job placeholder

Acceptance criteria:
- admin uploads PDF
- file exists in MinIO
- metadata exists in PostgreSQL
- user without permission cannot access another tenant document
```

---

## 6. Sprint 6 Prompt: Secure RAG Chat

```text
Implement the first secure RAG chat endpoint.

Target modules:
- rag
- chat
- providers/llm
- providers/vector_store

Expected files:
- ChatConversation model
- ChatMessage model
- RAG retrieval service
- Qdrant retriever
- Ollama LLM provider
- prompt template
- POST /api/v1/chat/query
- tests for access filtering

Rules:
- resolve user permissions before retrieval
- Qdrant filter must include tenant_id
- Qdrant filter must include access scopes allowed for the user
- never pass unauthorized chunks to the LLM
- if no source is found, return a refusal message
- include citations in the response

Acceptance criteria:
- user receives answer from authorized document
- user cannot retrieve another user's private document
- answer includes citations
- no-source questions are refused
```

---

## 7. Frontend Prompt Pattern

```text
Implement the Vue 3 frontend view for [feature].

Stack:
- Vue 3 Composition API
- TypeScript
- Pinia
- Bootstrap 5
- Bootstrap Icons

Rules:
- no business logic in components
- use typed API client
- use Pinia store for state
- keep layout professional and responsive
- handle loading, empty, error, and success states
- do not hardcode COMBIS

Acceptance criteria:
- view renders cleanly
- API integration works
- route guard respects auth state
- component is reusable where possible
```

---

## 8. Security Review Prompt

```text
Review the current implementation for security issues.

Focus on:
- tenant isolation
- RBAC enforcement
- document access filtering
- prompt injection exposure
- unsafe file upload handling
- secrets in repository
- missing audit logs

Output:
- list of issues
- severity
- affected files
- recommended patch
- tests to add

Do not rewrite everything. Propose small patches.
```

---

## 9. Refactoring Prompt Pattern

```text
Refactor [module] to improve architecture.

Rules:
- preserve public API contracts unless explicitly stated
- preserve tenant isolation
- preserve tests or update them if behavior changes
- do not introduce global state
- document the decision in docs/adr if architecture changes

Acceptance criteria:
- tests pass
- code is smaller or clearer
- no unrelated files modified
```

---

## 10. Documentation Update Prompt

```text
Update documentation after the implementation of [feature].

Update:
- README.md if setup changed
- docs/architecture if design changed
- docs/sprints if sprint status changed
- docs/adr if a major decision was made

Rules:
- be concise
- include commands when useful
- keep documentation accurate
```
