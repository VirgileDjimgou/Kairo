# Kairo Constitution

This file is the simple entry point for any agentic IDE session.

## Purpose

Kairo, also positioned as OrgMind AI, is a local-first multi-tenant RAG platform for organizations such as associations, clubs, NGOs, and small businesses.

The product must let each tenant:

- manage users, roles, and permissions
- upload and organize internal documents
- ingest and index those documents safely
- ask questions and receive grounded answers with citations
- enforce tenant isolation and access control before retrieval
- run locally through Docker Compose
- expose the app remotely through Cloudflare Tunnel when needed

## Hard Rules

- Never hardcode COMBIS or any tenant-specific product logic.
- Every tenant-scoped query must include `tenant_id`.
- The backend is the only policy enforcement point.
- The LLM never decides access control.
- Retrieval filtering must happen before prompt assembly.
- Never send unauthorized chunks to the LLM.
- The frontend consumes API contracts only.
- Use provider abstractions for storage, embeddings, vector search, parsers, and LLMs.
- Keep the modular monolith structure unless a documented decision justifies change.
- Update tests and docs when behavior changes.

## Canonical Deep Sources

When more detail is needed, read these files:

- `orgmind_prompt_pack/01_PROJECT_CONSTITUTION.md`
- `orgmind_prompt_pack/02_ARCHITECTURE.md`
- `orgmind_prompt_pack/03_ROADMAP_SPRINTS.md`
- `orgmind_prompt_pack/08_DATA_MODEL.md`
- `orgmind_prompt_pack/09_SECURITY_AND_LLM_SAFETY.md`

## Session Recovery Rule

At the start of every coding session, the agent must:

1. Read this constitution.
2. Read `IMPLEMENTATION_ROADMAP.md`.
3. Read `PROJECT_STATUS.md`.
4. Read `prompts/CODEX_AUTOPILOT.md`.
5. Inspect the current Git status.
6. Determine the current sprint.
7. Continue only the current sprint or the next unfinished sprint.

The agent must not rely on prior chat memory alone.
