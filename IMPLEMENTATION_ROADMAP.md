# Implementation Roadmap

This roadmap is the executable sprint plan for Kairo. Each sprint must be completed independently and the status files must be updated before the next sprint starts.

## Completion Rules

A sprint is complete only when:

- relevant build checks pass
- relevant tests pass
- documentation is updated
- architecture boundaries are preserved
- tenant isolation is preserved
- unresolved critical risks are explicitly listed
- `PROJECT_STATUS.md` reflects the new state

## Sprint 0 - Foundation And Repository Skeleton

Status: Completed

Goal:
Establish the repository as a durable monorepo that any agentic IDE can resume safely.

## Sprint 1 - Identity, Tenancy And Auth

Status: Completed

Goal:
Implement the minimal security foundation with JWT auth, tenant membership, and role resolution.

## Sprint 2 - Professional Vue Layout

Status: Completed

Goal:
Build the first portfolio-grade user shell with login, dashboard, app layout, and admin layout.

## Sprint 3 - Document Upload And Object Storage

Status: Completed

Goal:
Allow authenticated tenant users to upload documents and persist document metadata plus stored originals.

## Sprint 4 - Ingestion Worker And Parsing

Status: Completed

Goal:
Extract text from supported uploaded documents and persist chunk-ready ingestion results.

## Sprint 5 - Embeddings And Qdrant Indexing

Status: Completed

Goal:
Embed document chunks and store tenant-scoped vector payloads in Qdrant.

## Sprint 6 - First RAG Chat

Status: Completed

Goal:
Implement the first secure retrieval and answer flow with citations.

Deliverables:

- `rag` module
- `chat` module
- first LLM provider abstraction
- Ollama generation provider
- permission-aware retrieval filter builder
- first chat query endpoint
- no-source refusal behavior
- tests for tenant and access-scope retrieval safety

## Sprint 7 - Admin RAG Controls

Status: Completed

Goal:
Give administrators operational control over document access, ingestion, and answer traceability.

## Sprint 8 - Membership And Contributions

Status: Next

Goal:
Add structured member and contribution records with self-view and privileged back-office views.

## Sprint 9 - Policies, Rules And Discipline

Status: Planned

Goal:
Support public policies and private disciplinary records with strict access control.

## Sprint 10 - Events And Announcements

Status: Planned

Goal:
Add calendar and announcement capabilities for tenant operations.

## Sprint 11 - Cloudflare Tunnel Deployment

Status: Planned

Goal:
Document and harden local-first remote exposure for demo and small production-like setups.

## Sprint 12 - Evaluation And AI Safety

Status: Planned

Goal:
Add prompt-injection tests, no-source answer rules, and retrieval safety verification.

## Sprint 13 - Demo Tenant And Portfolio Polish

Status: Planned

Goal:
Prepare a recruiter-friendly and client-friendly local demo.

## Sprint 14 - Multi-Channel Extensions

Status: Planned

Goal:
Add optional messaging and notification provider extensions without polluting the core product.

## Sprint 15 - Commercialization Baseline

Status: Planned

Goal:
Prepare onboarding, settings, observability, backup posture, and product readiness foundations.
