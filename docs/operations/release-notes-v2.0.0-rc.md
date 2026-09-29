# Kairo 2.0.0 Release Candidate — Release Notes

Release: `2.0.0-rc` (Roadmap V2, Sprints 100–118)
Date: 2026-09-27
Scope: web platform, FastAPI core, Flutter Android/Web client, self-hosted
deployment.

## Highlights

- **Architecture truth reset.** The modular monolith keeps thin routers,
  service orchestration and repository isolation; finance, identity,
  notifications, chat and domain events are decomposed into bounded contexts
  with unchanged public contracts (ADR-tracked).
- **Internal module registry.** Every backend module ships a `module.py`
  descriptor; routers, tenant module toggles, search providers, optional AI
  context providers, health hooks and navigation metadata compose from the
  registry (ADR-013). `GET /api/v1/modules` serves tenant- and
  capability-filtered navigation.
- **Capability-driven clients.** `/auth/me` and tenant memberships expose
  effective capabilities (ADR-008); the Vue client and Flutter client derive
  navigation and action visibility from capabilities, with a drift-checked
  fallback for older payloads. Tenant-specific role bundles can extend canonical
  roles with validated capabilities.
- **Unified notification convergence.** One policy/recipient pipeline writes a
  canonical inbox envelope; Web Push (VAPID) and Android FCM are replaceable
  transports with bounded retries and invalid-target disabling; sign-out revokes
  the device binding; deep links are allowlisted; `/notifications/health` and
  metrics expose pipeline state. Inbox rows are always committed with the
  business operation — push is best-effort.
- **Transactional outboxes.** Internal domain events decouple finance, audit and
  notification projections with idempotent handlers and deduplication keys;
  Celery retries pending events safely.
- **OpenAPI as the client contract.** `docs/api/openapi.json` is versioned and
  regenerated deterministically; CI blocks breaking changes; generated
  TypeScript/Dart types are drift-checked and client calls must map to documented
  operations (ADR-011).
- **Observability and performance.** `/health`, `/health/live`, `/health/ready`
  and `/metrics` cover backup freshness and both outboxes; Celery logs carry
  request correlation; a committed 200/1000-member performance baseline records
  p50/p95 latency and SQL statement counts with `npm run perf:check` (ADR-012).
- **Hardened release operations.** Encrypted, SHA-256-verified, signed recovery
  archives; daily backups and WAL archiving; backup-before-migration in the
  upgrade helper; a non-destructive restore drill script; deployment/rollback
  helpers and smoke checks.

## Clients

- Vue 3 PWA (production client): French-first i18n with EN/DE parity, role-aware
  navigation and action center, global permission-aware search, responsive
  member/finance/discipline/governance workspaces, accessibility fixes from the
  Sprint 118 audit (skip link, contrast, named progress bars).
- Flutter client (`apps/flutter_kairo`): Android and Flutter Web targets, feature
  parity tracked in `docs/flutter/FEATURE_PARITY.md`, secure storage, offline
  drafts, FCM/deep links and Material 3 light/dark themes. Release signing and
  Flutter Web promotion remain gated on operator credentials and explicit
  approval.

## Upgrade and rollback

1. Run `bash scripts/deploy_release.sh preflight`.
2. Run `bash scripts/deploy_release.sh upgrade` — creates the safety backup,
   rebuilds images, applies migrations and runs the smoke check.
3. Verify `alembic current` equals the release head and `/health` is green.
4. Roll back with `bash scripts/rollback_release.sh <backup-archive>` if a
   blocking regression is found; see `docs/operations/deployment-runbook.md`.

Do not skip the migration safety backup. The pre-migration backup must come from
the infrastructure path (`scripts/backup.sh`), because application-level backup
code runs against the new schema.

## Validation summary

See `docs/sprint-118-release-candidate-evidence.md`. Release-candidate gates:
362 backend tests, web type-check/build and 52 Chromium tests (locale, roles,
release-candidate, accessibility), Flutter analysis plus 52 tests and both
release builds, OpenAPI/generated-contract checks, repository guards, an upgrade
from revision 0029 to 0033 with data preserved, a passing encrypted-archive
restore drill, and a passing rollback restore of the pre-upgrade dump.

## Known issues and intentional limits

- Permanent member deletion is deferred from the first Flutter pilot; the PWA is
  the role-gated fallback.
- Flutter Web is staging-only until an authorised operator promotes a separate
  Cloudflare hostname; the PWA hostname is unchanged.
- Some admin Vue views still contain hardcoded English strings; tracked as a
  non-blocking i18n backlog item.
- Historical JWT secret rotation is `HUMAN_REQUIRED`
  (`docs/security/HISTORY_EXPOSURE_REPORT.md`).
- Android release signing fails closed until the association supplies its private
  upload keystore; no production deployment was performed by this sprint.
