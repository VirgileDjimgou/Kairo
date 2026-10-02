# ADR-006: Separate Flutter Client, PWA Stays Production

Status: Superseded by ADR-014 for client ownership and release targets. Retained
as the historical record of how the Flutter client was introduced.

## Context

A native Android experience with offline drafts and FCM is valuable, but the
Vue 3 PWA is the current production client used by the association.

## Decision

The Flutter client (`apps/flutter_kairo/`) is a separate application that
consumes the same FastAPI contracts. It never implements authorization locally,
never stores passwords, never bypasses tenant boundaries and never duplicates
backend business rules. The PWA is not replaced, wrapped or degraded by it.

## Consequences

- Android and Flutter Web are the first release targets; iOS/desktop stay
  architecture-ready until a roadmap decision promotes them.
- Feature parity is tracked in `docs/flutter/FEATURE_PARITY.md`.
- Any shared change (API contract) must keep both clients working (Roadmap V2
  S115 formalizes contract parity).
