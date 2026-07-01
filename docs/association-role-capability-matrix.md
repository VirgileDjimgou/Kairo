# Association Role Capability Matrix

Last updated: 2026-07-01

This document is the Sprint 41 governance foundation for the professional association track.

## Canonical Roles

- `principal_admin`
- `president`
- `vice_president`
- `secretary_general`
- `treasurer`
- `auditor`
- `censor`
- `sports_manager`
- `member`

## Legacy Compatibility

- The legacy `admin` role remains supported during the transition track.
- For backend capability checks, legacy `admin` currently maps to the same broad capability surface as `principal_admin`.
- The explicit migration away from legacy `admin` semantics is deferred to Sprint 49.

## Capability Matrix

| Role | Core intent | Main capabilities |
| --- | --- | --- |
| `principal_admin` | Full tenant operator | tenant administration, role assignment, audit read, tenant settings write, all major read/write domains |
| `president` | Executive oversight | finance read/audit, membership directory read, governance document read, sanctions overview read, audit read |
| `vice_president` | Deputy oversight | cross-module read access with narrower oversight than president |
| `secretary_general` | Governance records owner | document write, policy write, announcement write, governance-oriented read access |
| `treasurer` | Finance operator | finance read/write, member directory read, member self read |
| `auditor` | Finance oversight | finance read/audit, audit read, export-sensitive read, governance read |
| `censor` | Discipline and compliance | disciplinary read/write, membership read, governance read |
| `sports_manager` | Sports operations | event read/write, lightweight announcement read |
| `member` | Ordinary member self-service | personal membership read, personal finance read, events, policies, announcements, and documents read |

## Security Notes

- Capabilities are backend-derived from tenant-scoped role claims.
- The frontend may adapt navigation, but it never decides authorization.
- Structured role-driven route refactors are intentionally deferred to Sprint 42.
- Multi-tenant isolation still depends on `tenant_id` filtering and backend membership checks on every protected request.
