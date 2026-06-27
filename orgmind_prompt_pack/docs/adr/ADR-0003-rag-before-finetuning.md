# ADR-0003 - Use RAG Before Fine-tuning

## Status

Accepted

## Context

The assistant must answer from changing organizational documents. Fine-tuning is not ideal for rapidly changing facts, private records, or access-controlled knowledge.

## Decision

Implement RAG first. Fine-tuning may be considered later only for tone, formatting, and task behavior, not for storing confidential facts.

## Consequences

Positive:

- answers remain tied to current sources
- easier updates
- citations are possible
- access control is enforceable

Negative:

- retrieval quality must be carefully engineered
- document ingestion and metadata quality are critical
