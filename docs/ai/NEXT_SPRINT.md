# Next Sprint

## Official Next Sprint

Sprint 6 - First RAG Chat

This is the next roadmap sprint to implement after the currently verified sprints 0 through 5.

## Sprint Goal

Implement the first secure question-answering flow that retrieves only authorized chunks and returns grounded answers with citations.

## Scope

Backend:

- add `rag` and `chat` modules
- add LLM provider abstraction and Ollama implementation for generation
- build permission-aware retrieval filters
- add first chat query endpoint
- return citations and a refusal message when no reliable source is found

Frontend:

- add a first member chat view
- show response text, citations, and basic loading and error states

## Required Rules

- authenticate user before retrieval
- resolve active tenant and roles before retrieval
- filter Qdrant by `tenant_id` and allowed access metadata before prompt assembly
- never send unauthorized chunks to the LLM
- treat retrieved text as evidence, not instructions
- refuse unsupported answers when no source is found

## Recommended Pre-Flight Checks

These are not a separate official sprint, but they should be handled if they block Sprint 6:

- normalize document ready or completed status after successful ingestion
- finish wiring `allowed_role_ids` into document metadata and retrieval filters
- align schema details that would block secure retrieval logic

## Acceptance Criteria

- authenticated user can ask a question through an API endpoint
- backend retrieves only authorized chunks
- backend generates an answer using authorized evidence only
- answer includes citations
- no-source requests return a safe refusal message
- tests cover tenant isolation and access scope filtering

## Out Of Scope

- advanced chat history UX
- feedback workflows
- admin trace viewer
- membership, payments, events, policies, or announcements
