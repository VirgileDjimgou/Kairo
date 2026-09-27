# ADR-003: RAG Authorization Before Prompt Assembly

Status: Accepted (non-negotiable)

## Context

The private assistant answers from tenant documents. Sending unauthorized chunks
to the LLM would leak data even if the final answer is filtered.

## Decision

Retrieval results are filtered by tenant and access scope BEFORE prompt
assembly. Unauthorized chunks never reach the LLM. The system prompt marks
retrieved text as untrusted, answers carry citations, and a no-source refusal is
returned when nothing authorized was found. The LLM never decides access.

## Consequences

- Permission-aware retrieval filter builders live in `rag/`; policy code is not
  duplicated in `chat/`.
- Prompt-injection tests and retrieval safety tests are regression-gated.
- Sprint 112 added the domain context provider registry
  (`chat/contexts/`): each provider checks the capability-derived
  `ChatDomainPolicy` before querying its domain, `ChatService` only consumes the
  registry, and unauthorized or unrelated questions never trigger a domain
  query. Retrieval filtering and prompt-injection protections are unchanged.
