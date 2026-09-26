# ADR-001: Modular Monolith

Status: Accepted (records the existing architecture; reaffirmed by Roadmap V2)

## Context

Kairo must stay operable by a small team and a single self-hosted deployment
while its module count grows. Early sprints built one FastAPI application with
module packages.

## Decision

Keep a single deployable backend (FastAPI modular monolith) with explicit module
boundaries (`core/`, `identity/`, `tenancy/`, `membership/`, `contributions/`,
`documents/`, `rag/`, `chat/`, `notifications/`, `audit/`, `backup/`, `worker/`).
Decoupling happens through internal seams (services, contracts, domain events,
outbox), not through network services.

## Consequences

- One transaction boundary, one deployment, simple operator story.
- Module boundaries must be enforced by convention and review; Roadmap V2 S117
  adds a registry to make them mechanical.
- Introducing microservices or a broker like Kafka is out of scope; a documented
  ADR would be required to change this.
