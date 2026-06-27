# Brainstorming Summary for OrgMind AI

## 1. Starting Point

The original idea was to build a WhatsApp-oriented assistant for COMBIS. The assistant would ingest association documents and answer members' questions about contributions, statutes, rules, sanctions, events, and internal decisions.

The initial COMBIS use case exposed several recurring problems:

- contribution lists are difficult to keep accurate
- members need transparent access to their own payment status
- rules are spread across multiple documents
- WhatsApp communication creates misunderstandings
- board decisions are not always easy to retrieve
- disciplinary rules need consistent explanation
- members should not access private data belonging to other members

## 2. Evolution of the Idea

The project evolved from a simple COMBIS bot into a generic multi-tenant RAG platform.

Instead of building a COMBIS-only tool, the decision was made to create a reusable product that can work for many contexts:

- associations
- sports clubs
- cultural communities
- NGOs
- small businesses
- internal teams
- training centers

COMBIS becomes the first real demonstration tenant, not the hardcoded target.

## 3. Core Product Direction

The selected product direction is:

> A local-first, secure, multi-tenant AI knowledge assistant for organizations.

The system must allow each organization to:

- upload internal documents
- manage users and roles
- define access permissions
- ask questions through a web portal
- receive source-backed answers
- manage structured records such as contributions, events, rules, and policies
- run locally with minimal or zero cost
- expose the system through Cloudflare Tunnel

## 4. Hosting Decision

Firebase was considered as a possible intermediary between clients and a local server. The final recommendation is not to use Firebase as the core architecture.

The selected approach is:

```text
User Browser
   ↓
Cloudflare Tunnel
   ↓
Local Machine
   ↓
Docker Compose Stack
```

Reasons:

- avoids Firebase dependency
- keeps a real API architecture
- preserves backend control
- avoids mandatory cloud cost
- keeps data local
- is better for a professional portfolio

## 5. Frontend Decision

The frontend stack is fixed as:

- Vue 3
- TypeScript
- Pinia
- Bootstrap 5
- Vite

The UI must be elegant, modern, and professional. It should look like a serious SaaS product, not a quick prototype.

Main UI sections:

- Login
- Member portal
- AI chat
- My records
- Documents
- Admin dashboard
- Users and roles
- Ingestion jobs
- Contributions
- Events
- Policies
- Audit logs
- Settings

## 6. Backend Decision

The backend should be Python-based:

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- PostgreSQL
- Redis worker

The backend is responsible for:

- authentication
- authorization
- tenant isolation
- document ingestion
- RAG retrieval
- LLM orchestration
- structured business modules
- audit logging

## 7. AI and RAG Decision

The AI layer should be local-first:

- Ollama for local LLMs
- Qdrant for vector search
- local embeddings where possible
- remote LLM providers optional later

The RAG pipeline must be permission-aware.

Critical rule:

```text
Permission filtering happens before vector retrieval and before LLM prompt assembly.
```

## 8. Security Direction

Security is central because the system may contain sensitive organizational data.

Important controls:

- tenant isolation
- RBAC
- document access scopes
- private member data protection
- audit logging
- source-backed AI answers
- prompt injection resistance
- file validation
- no secrets in Git

The LLM must never be trusted to enforce security.

## 9. Architecture Direction

The selected architecture is:

```text
Modular monolith backend + separate infrastructure services
```

This is better than microservices at the beginning because:

- simpler local deployment
- easier Docker Compose setup
- easier development with Codex/Copilot
- fewer moving parts
- enough modularity for future growth

## 10. Portfolio Direction

The project must be designed as a GitHub portfolio piece.

It should demonstrate:

- full-stack engineering
- AI/RAG engineering
- security-aware architecture
- Docker deployment
- multi-tenant design
- professional frontend design
- documentation discipline
- product thinking

Suggested GitHub names:

- orgmind-ai
- secure-rag-platform
- association-ai-platform
- tenantwise-rag
- civic-rag-assistant

## 11. Product Finality

The final product should become:

> A commercializable local-first AI workspace for small organizations that want private knowledge retrieval without paying for heavy SaaS infrastructure.

The first commercial angle:

- associations and clubs
- small businesses with internal procedures
- communities with rules and member data
- organizations needing a low-cost private assistant

## 12. Implementation Strategy

The project must be built sprint by sprint.

Rules:

- do not ask Codex to build everything at once
- implement vertical slices
- keep docs updated
- test core logic
- preserve tenant isolation
- preserve provider abstraction
- keep local deployment working
- use COMBIS only as demo data

## 13. Key Product Modules

Initial modules:

- Identity and Access
- Tenancy
- Documents
- Ingestion
- RAG Chat
- Admin Dashboard
- Membership
- Contributions
- Events
- Policies
- Audit
- Deployment

Future modules:

- Telegram bot
- WhatsApp official API integration
- email notifications
- analytics
- answer evaluation
- SaaS onboarding

## 14. Final Positioning

OrgMind AI should be presented as:

```text
A local-first, multi-tenant RAG platform for associations and small organizations, built with FastAPI, Vue 3, PostgreSQL, Qdrant, MinIO, Ollama, Docker, and Cloudflare Tunnel.
```
