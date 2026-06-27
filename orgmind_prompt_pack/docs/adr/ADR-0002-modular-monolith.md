# ADR-0002 - Use Modular Monolith First

## Status

Accepted

## Context

The product has many modules: identity, documents, ingestion, RAG, chat, contributions, policies, events, and audit. Microservices would add complexity too early.

## Decision

Implement the backend as a modular monolith in FastAPI with clear module boundaries.

## Consequences

Positive:

- simpler development
- easier local Docker deployment
- easier testing
- easier for Codex/Copilot to understand
- lower operational complexity

Negative:

- all modules initially share one deployment lifecycle
- scaling is coarse-grained

## Extraction Rule

A module may become a separate service only when it has a strong independent scaling or operational reason.
