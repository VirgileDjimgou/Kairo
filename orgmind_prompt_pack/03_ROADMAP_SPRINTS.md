# OrgMind AI Roadmap by Sprints

This roadmap is designed for 100% vibe coding with Codex Desktop or GitHub Copilot. Each sprint must produce a working vertical slice or a stable foundation.

---

## Sprint 0 - Foundation and Repository Skeleton

Goal:
Create the project base and make the repo understandable for AI coding tools.

Deliverables:

- monorepo structure
- README.md
- docs scaffold
- Docker Compose skeleton
- FastAPI health endpoint
- Vue 3 app shell
- `.env.example`
- basic CI workflow
- initial architecture docs

Acceptance criteria:

- `docker compose up` starts core services or placeholders
- API exposes `/health`
- frontend opens successfully
- docs explain the project purpose

---

## Sprint 1 - Identity, Tenancy and Auth

Goal:
Implement the minimal security foundation.

Deliverables:

- Tenant model
- User model
- Role model
- Permission model
- JWT login
- password hashing
- tenant-aware dependencies
- seed admin user

Acceptance criteria:

- user can login
- API knows active tenant
- protected endpoint rejects unauthenticated requests
- tenant_id is required in scoped operations

---

## Sprint 2 - Professional Vue Layout

Goal:
Build a clean and elegant professional interface.

Deliverables:

- login page
- app layout
- admin layout
- sidebar navigation
- topbar
- tenant selector placeholder
- dashboard cards
- Pinia auth store
- typed API client

Acceptance criteria:

- UI is responsive
- Bootstrap 5 is integrated
- protected routes work
- layout looks portfolio-grade

---

## Sprint 3 - Document Upload and Object Storage

Goal:
Allow admins to upload documents.

Deliverables:

- MinIO integration
- Document model
- DocumentVersion model
- upload API
- access scope fields
- admin documents page
- document list
- ingestion status placeholder

Acceptance criteria:

- admin uploads a file
- file stored in MinIO
- metadata stored in PostgreSQL
- document appears in dashboard

---

## Sprint 4 - Ingestion Worker and Parsing

Goal:
Extract text from uploaded documents.

Deliverables:

- worker service
- ingestion job model
- PDF parser
- DOCX parser
- TXT/Markdown parser
- WhatsApp TXT parser
- basic OCR placeholder
- chunking service

Acceptance criteria:

- uploaded PDF produces chunks
- ingestion job status is visible
- failures are logged and visible

---

## Sprint 5 - Embeddings and Qdrant Indexing

Goal:
Index chunks into vector database.

Deliverables:

- embedding provider interface
- local embedding implementation
- Qdrant provider
- collection creation
- chunk metadata payloads
- tenant/access metadata filters

Acceptance criteria:

- document chunks are embedded
- Qdrant payload includes tenant_id and access_scope
- indexing is repeatable

---

## Sprint 6 - First RAG Chat

Goal:
Implement secure question answering with citations.

Deliverables:

- chat endpoint
- retrieval filter builder
- LLM provider interface
- Ollama provider
- prompt template
- citation output
- member chat UI

Acceptance criteria:

- user asks a question
- backend retrieves authorized chunks only
- answer includes sources
- answer refuses when no source is found

---

## Sprint 7 - Admin RAG Controls

Goal:
Give administrators control over the knowledge base.

Deliverables:

- document access scope editor
- re-ingest action
- delete/archive document
- ingestion job monitor
- answer trace view
- chat feedback buttons

Acceptance criteria:

- admin can update access scope
- RAG results change based on permissions
- answer trace shows retrieved sources

---

## Sprint 8 - Membership and Contributions Module

Goal:
Add structured organizational records.

Deliverables:

- MembershipProfile model
- ContributionRecord model
- PaymentRecord model
- member self-view
- treasurer/admin list
- balance calculation
- CSV import placeholder

Acceptance criteria:

- member sees only personal balance
- treasurer sees all balances
- admin can import or add contribution records

---

## Sprint 9 - Policies, Rules and Discipline Module

Goal:
Support association/business policies and procedures.

Deliverables:

- PolicyRecord model
- DisciplinaryRecord model
- rule category management
- private disciplinary records
- role-based access rules

Acceptance criteria:

- user can ask about public policies
- user cannot see another user's disciplinary record
- admins can manage policy documents

---

## Sprint 10 - Events and Announcements

Goal:
Add operational communication features.

Deliverables:

- Event model
- Announcement model
- event calendar view
- announcement board
- visibility scopes
- reminder placeholder

Acceptance criteria:

- members see public events
- role-restricted announcements are hidden from unauthorized users

---

## Sprint 11 - Cloudflare Tunnel Deployment

Goal:
Make local hosting externally reachable for demos.

Deliverables:

- cloudflared config sample
- deployment guide
- reverse proxy config sample
- CORS setup
- production `.env.example`
- local backup script docs

Acceptance criteria:

- user can expose local app through Cloudflare Tunnel
- docs explain setup clearly
- no secrets are committed

---

## Sprint 12 - Evaluation and AI Safety

Goal:
Improve trust and security.

Deliverables:

- prompt injection tests
- access control tests
- retrieval evaluation set
- answer quality rubric
- no-source refusal tests
- audit review screen

Acceptance criteria:

- tests confirm private data is not retrieved
- prompt injection examples do not override rules
- answer quality can be reviewed

---

## Sprint 13 - Demo Tenant and Portfolio Polish

Goal:
Make the project GitHub-ready.

Deliverables:

- demo tenant seed
- anonymized COMBIS-style sample data
- screenshots
- README polish
- architecture diagram
- quickstart guide
- demo script

Acceptance criteria:

- a recruiter can understand the project in 2 minutes
- demo runs locally
- screenshots show professional UI

---

## Sprint 14 - Multi-channel Extensions

Goal:
Add optional channels after web product works.

Deliverables:

- Telegram provider placeholder
- WhatsApp provider placeholder
- Email provider placeholder
- notification abstraction

Acceptance criteria:

- web remains primary channel
- providers are optional and do not pollute core logic

---

## Sprint 15 - Commercialization Baseline

Goal:
Prepare for real users and possible commercialization.

Deliverables:

- onboarding flow
- tenant settings
- module toggles
- backup/restore scripts
- basic observability
- product landing README section
- license decision

Acceptance criteria:

- product can be presented as commercializable MVP
- deployment and backup are documented
- tenant settings control enabled modules
