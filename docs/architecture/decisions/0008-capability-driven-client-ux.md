# ADR-008: Capability-Driven Client UX With Backend Enforcement

Status: Accepted

## Context

Roles are useful named bundles, but the Vue and Flutter clients previously
repeated hardcoded role-name lists to decide which navigation entries and quick
actions to render. With canonical roles plus future tenant-specific bundles, the
duplication becomes a maintenance and drift risk.

## Decision

- The backend owns an authoritative capability catalog
  (`services/api/app/core/capabilities.py`, `modules/tenancy/role_catalog.py`).
- Effective capabilities are exposed read-only through the existing auth
  contract: `GET /auth/me` returns `capabilities` for the active tenant and each
  `memberships[]` entry carries `capabilities` for its tenant. Tenant switching
  therefore updates capabilities with the membership list.
- Clients consume capabilities for navigation and action visibility. Canonical
  roles remain valid bundles and may still be read for labels and bundle
  identity, but client-side role arrays must not drive visibility.
- Adding or changing a capability never relaxes backend authorization: every
  endpoint keeps enforcing its existing capability, role, tenant and module
  dependencies. Client capability checks are presentation-only.
- Two capabilities are explicitly presentation-scoped
  (`governance:cockpit_read`, `disciplinary:oversight_read`); they are never
  referenced by an authorization dependency.

## Consequences

- The web client derives navigation from capabilities and only falls back to a
  generated, drift-checked role bundle map when an older or mocked payload omits
  `capabilities` (`scripts/check-capability-bundles.mjs` fails CI on drift).
- Flutter consumes the same additive contract; the fields are optional and no
  existing response shape was removed.
- Tenant-specific bundles become possible without shipping new client lists.
