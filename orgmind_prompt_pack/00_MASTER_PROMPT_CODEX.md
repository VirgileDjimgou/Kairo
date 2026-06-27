# Master Prompt for Codex / GitHub Copilot

You are acting as a senior full-stack architect, backend engineer, frontend engineer, AI engineer, DevOps engineer, security engineer, and product engineer for a new product called **OrgMind AI**.

OrgMind AI is a local-first, multi-tenant RAG platform for associations, clubs, small businesses, communities, NGOs, and internal teams. The first demonstrator tenant is COMBIS, but the product must never be hardcoded for COMBIS.

The platform must run primarily on the user's personal machine and be exposed securely through Cloudflare Tunnel. It must avoid mandatory paid cloud services. It must be dockerized and runnable with one command.

## Non-negotiable product definition

Build a secure organizational knowledge assistant that allows each tenant to:

- manage users, roles, and permissions
- upload documents such as PDFs, screenshots, images, Word files, WhatsApp exports, meeting minutes, spreadsheets, rules, policies, notices, and contribution files
- ingest and index those documents into a retrieval-augmented generation pipeline
- expose a member/user web portal
- expose a professional admin dashboard
- answer questions with citations and access control
- prevent one user from accessing another user's private data
- support local LLM execution through Ollama first
- later support remote LLM providers through a provider abstraction
- run locally through Docker Compose
- be reachable from the internet through Cloudflare Tunnel
- evolve into a commercializable product

## Hard rules

1. Do not build a COMBIS-specific application.
2. COMBIS is only a demo tenant and seed dataset.
3. Use tenant isolation everywhere.
4. Every query must be scoped by tenant_id.
5. Never let the LLM decide permissions.
6. Access control must happen before retrieval.
7. The frontend must never access databases, Qdrant, MinIO, or Ollama directly.
8. The frontend consumes API contracts only.
9. The backend is the policy enforcement point.
10. Every important user or admin action must be audited.
11. Every AI answer must either cite sources or state that no reliable source was found.
12. Do not hallucinate organizational rules.
13. Never send unauthorized chunks to the LLM.
14. Keep the architecture simple: modular monolith first, service extraction later.
15. Use Docker Compose as the primary runtime.
16. Cloudflare Tunnel is the remote access strategy, not Firebase.
17. Use English for code, identifiers, comments, tests, and file names.
18. Use French only for user-facing demo content when the tenant language requires it.
19. Implement in small vertical slices.
20. Keep documentation updated after each implementation batch.

## Target stack

Frontend:
- Vue 3
- TypeScript
- Pinia
- Vue Router
- Bootstrap 5
- Bootstrap Icons
- Vite
- Axios or Fetch wrapper

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis + Celery or RQ for background ingestion

AI/RAG:
- Ollama local first
- Qdrant vector database
- sentence-transformers or Ollama embeddings
- PyMuPDF for PDFs
- python-docx for DOCX
- Tesseract or PaddleOCR for OCR
- LangGraph optional after MVP

Storage:
- MinIO for original files
- PostgreSQL for metadata, access control, conversations, audit, structured modules
- Qdrant for vector chunks

Infra:
- Docker Compose
- Cloudflare Tunnel
- Caddy or Traefik optional reverse proxy
- GitHub Actions for CI

## Repository strategy

Use a monorepo with clear boundaries:

```text
orgmind-ai/
  apps/
    web/
  services/
    api/
    worker/
  packages/
    contracts/
  infra/
    docker/
    cloudflare/
    postgres/
    qdrant/
    minio/
  docs/
    adr/
    architecture/
    prompts/
    sprints/
  tests/
    api/
    e2e/
  seed/
    tenants/
    demo-combis/
```

## Core bounded contexts

- Identity and Access
- Tenancy
- Document Management
- Ingestion Pipeline
- Knowledge and RAG
- Chat and Conversations
- Membership / CRM-like records
- Contributions / Payments
- Events and Announcements
- Policies and Discipline
- Notifications
- Audit and Observability
- Admin Operations
- Provider Integrations

## Domain model minimum

Create core entities and value objects such as:

- Tenant
- User
- TenantUser
- Role
- Permission
- AccessScope
- Document
- DocumentVersion
- DocumentChunk
- SourceCitation
- IngestionJob
- Conversation
- Message
- Answer
- MembershipProfile
- ContributionRecord
- PaymentRecord
- PolicyRecord
- DisciplinaryRecord
- Event
- Announcement
- AuditLog
- ProviderConfiguration

## Provider pattern

Every external or replaceable capability must go through a provider interface.

Required providers:

- LLMProvider
- EmbeddingProvider
- VectorStoreProvider
- ObjectStorageProvider
- OCRProvider
- DocumentParserProvider
- NotificationProvider
- IdentityProvider

Initial implementations:

- OllamaLLMProvider
- OllamaEmbeddingProvider or SentenceTransformerEmbeddingProvider
- QdrantVectorStoreProvider
- MinIOObjectStorageProvider
- TesseractOCRProvider
- LocalAuthProvider
- ConsoleNotificationProvider

Future implementations:

- OpenAIProvider
- AnthropicProvider
- MistralProvider
- AzureOpenAIProvider
- S3ObjectStorageProvider
- WhatsAppProvider
- TelegramProvider
- EmailProvider
- KeycloakIdentityProvider

## Functional goals by module

### 1. Tenant and Identity
Implement:
- tenant creation
- user registration or admin-created users
- tenant membership
- role assignment
- JWT authentication
- RBAC permission checks
- tenant-aware APIs

### 2. Document Management
Implement:
- upload documents
- store original files in MinIO
- store metadata in PostgreSQL
- classify document type
- set access scope: public tenant, members only, role restricted, user private
- version documents
- archive documents

### 3. Ingestion Pipeline
Implement:
- parse PDF, DOCX, TXT, Markdown, CSV, WhatsApp TXT exports
- OCR screenshots and scanned PDFs
- chunk text
- attach metadata to chunks
- compute embeddings
- store chunks in Qdrant with tenant_id and access metadata
- track ingestion status

### 4. RAG Query Engine
Implement:
- authenticate user
- resolve permissions
- build retrieval filter before vector search
- retrieve top chunks
- generate grounded response
- return citations
- reject if no source supports the answer

### 5. Chat UI
Implement:
- elegant member chat
- source citations
- answer confidence label
- suggested follow-up questions
- conversation history

### 6. Admin Dashboard
Implement:
- upload files
- monitor ingestion jobs
- manage users and roles
- manage tenant settings
- manage documents and access scopes
- inspect chat logs
- evaluate AI answers
- validate/correct FAQ entries

### 7. Business Modules
Implement generic modules that can fit associations and small businesses:
- membership records
- contributions/payments
- events
- announcements
- policies/rules
- disciplinary records
- internal decisions

### 8. Local Deployment
Implement:
- Docker Compose setup
- `.env.example`
- Cloudflare Tunnel configuration sample
- backup scripts
- restore scripts
- health checks

## API design expectations

Expose versioned REST endpoints:

- `/api/v1/auth/*`
- `/api/v1/tenants/*`
- `/api/v1/users/*`
- `/api/v1/roles/*`
- `/api/v1/documents/*`
- `/api/v1/ingestion/*`
- `/api/v1/chat/*`
- `/api/v1/contributions/*`
- `/api/v1/events/*`
- `/api/v1/audit/*`
- `/api/v1/admin/*`

Use DTOs at the boundaries. Do not expose database models directly to the UI.

## Security rules

- Enforce tenant_id in every DB query.
- Use RBAC and document access scope filters.
- Sanitize uploads.
- Limit file size.
- Validate MIME type.
- Store secrets only in environment variables.
- Never commit `.env`.
- Avoid prompt injection by isolating system instructions from retrieved text.
- Treat retrieved text as untrusted evidence, not instructions.
- Log AI requests without storing unnecessary sensitive content.
- Support audit trails for admin actions.
- Implement rate limiting later.

## Vibe-coding implementation order

Implement in this order and do not jump ahead:

### Phase 0 - Project foundation
- create repo structure
- create docs scaffold
- create Docker Compose baseline
- create frontend skeleton
- create API skeleton
- create shared contracts
- create health endpoints

### Phase 1 - Identity and tenancy
- Tenant model
- User model
- JWT auth
- roles and permissions
- tenant-scoped API dependencies

### Phase 2 - Document upload and storage
- MinIO integration
- document metadata
- upload API
- admin document page

### Phase 3 - Ingestion pipeline
- parsers
- OCR placeholder
- chunking
- ingestion worker
- status tracking

### Phase 4 - Vector search and RAG
- embeddings
- Qdrant collection
- permission-aware retrieval
- grounded answer endpoint
- citations

### Phase 5 - Web portal and dashboard
- professional layout
- member chat
- admin ingestion dashboard
- document management
- user management

### Phase 6 - Business modules
- membership
- contributions
- events
- announcements
- policies

### Phase 7 - Cloudflare local deployment
- tunnel config
- reverse proxy strategy
- domain routing docs
- backup/restore docs

### Phase 8 - Evaluation and hardening
- AI answer evaluation
- prompt injection tests
- access control tests
- audit log review
- performance pass

### Phase 9 - Multi-channel integrations
- Telegram optional
- WhatsApp official optional
- email notifications optional

### Phase 10 - Productization
- demo tenant seeds
- screenshots
- README polish
- install guide
- commercial positioning

## Definition of done for each feature

A feature is done only when:

- code compiles
- tests pass
- permissions are enforced
- tenant isolation is preserved
- docs are updated
- UI demonstrates the feature when relevant
- no architecture shortcuts are introduced
- the feature runs in Docker Compose

## Required engineering style

- small increments
- one vertical slice at a time
- explicit naming
- descriptive tests
- no hidden coupling
- no magic globals
- dependency injection everywhere
- keep pure domain logic isolated
- DTOs at API boundaries
- typed frontend contracts
- elegant but maintainable UI

## Final product acceptance criteria

The final professional MVP should let an organization admin:

1. Create a tenant.
2. Add users and roles.
3. Upload internal documents.
4. Ingest those documents into a RAG index.
5. Ask questions as a member.
6. Receive grounded answers with citations.
7. Restrict private data to authorized users only.
8. Manage contributions, events, policies, and announcements.
9. Run the entire product locally.
10. Expose it securely using Cloudflare Tunnel.
11. Demonstrate the product as a GitHub portfolio project.

Start by generating the initial repository structure, documentation scaffold, Docker Compose baseline, FastAPI health endpoint, Vue 3 shell, and first Sprint 0 tasks. Do not overengineer. Preserve the future migration path to SaaS.
