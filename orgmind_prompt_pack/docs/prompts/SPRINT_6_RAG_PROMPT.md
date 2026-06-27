# Sprint 6 Secure RAG Prompt

Implement permission-aware RAG chat.

Read first:
- 00_MASTER_PROMPT_CODEX.md
- 01_PROJECT_CONSTITUTION.md
- 02_ARCHITECTURE.md
- 08_DATA_MODEL.md
- 09_SECURITY_AND_LLM_SAFETY.md

Target modules:
- rag
- chat
- providers/llm
- providers/vector_store

Implement:
- retrieval filter builder
- Qdrant vector retrieval
- Ollama LLM provider
- chat query endpoint
- citations response model
- no-source refusal behavior
- tests for private data isolation

Rules:
- backend decides permissions
- Qdrant retrieval must filter by tenant_id and allowed scopes
- never send unauthorized chunks to LLM
- citations are mandatory when sources exist

Acceptance criteria:
- authorized document question returns answer with citations
- unauthorized document is not retrieved
- no evidence returns refusal
