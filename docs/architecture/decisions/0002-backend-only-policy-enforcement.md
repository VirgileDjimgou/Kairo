# ADR-002: Backend Is The Only Policy Enforcement Point

Status: Accepted (non-negotiable)

## Context

Kairo serves multiple tenants with office roles (treasurer, censor, secretary
general, auditor, …). Clients must never be able to grant themselves access.

## Decision

Roles, capabilities, tenant isolation and module entitlements are enforced in
FastAPI (dependencies, services, repositories). Frontends consume API contracts
and use role/capability information for presentation only. The LLM never decides
access control.

## Consequences

- Every tenant-scoped query includes `tenant_id`.
- UI permission checks are convenience only and are always backed by server
  checks; security tests assert the server behavior.
- No frontend code may become the authority for authorization (Roadmap V2 S109
  keeps this invariant when clients move to capability-driven UI).
