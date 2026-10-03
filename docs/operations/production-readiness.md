# Production Readiness And Recovery

This document captures the validation steps for Sprint 24.

The preferred operator flow now starts with [`docs/operations/deployment-runbook.md`](./deployment-runbook.md), which wraps these checks into install, upgrade, and rollback helpers.

## 1. Production Build Validation

Run from the repository root:

```bash
bash scripts/deploy_release.sh preflight
bash scripts/deploy_release.sh install
```

Expected outcome:

- compose config renders without errors
- both production images build successfully
- the API container starts with production settings
- the web container serves the built SPA through nginx

## 2. Production Smoke Check

Once the stack is running:

```bash
bash scripts/production_smoke.sh http://localhost
```

Expected outcome:

- `/health` reports dependency status and module list
- `/metrics` returns runtime metrics text
- `/` serves the SPA entry point
- optional monitoring can scrape `/metrics` through the packaged Prometheus/Grafana baseline in `infra/monitoring/`

## 3. Backup And Restore Drill

Create a backup:

```bash
bash scripts/backup.sh ./backups
```

Restore drill outline:

1. Stop the stack.
2. Extract the backup archive.
3. Restore PostgreSQL first.
4. Restore Qdrant, MinIO, Redis, and Ollama data.
5. Start the stack again.
6. Verify `/health`, document listing, and chat/document flows.

Validation criteria:

- the database restores cleanly
- object storage files are present
- vector store files are restored
- the application boots after restoration
- tenant-scoped data remains intact

## 4. Recovery Evidence Capture

After every successful backup or restore drill, record the evidence inside the tenant settings screen or via the tenant operations command center; the new admin health center can then surface the same evidence alongside live dependency checks for quick operational review.

Record at least:

- last backup timestamp
- backup status and archive reference
- last restore drill timestamp
- restore drill status
- alert posture and whether contacts are configured
- a short note describing the latest drill outcome

Use the admin health center or the admin overview to confirm the recovery evidence status:

- `healthy` means the evidence is current and the alert posture is configured
- `warning` means the evidence exists but is aging or incomplete
- `critical` means the tenant has no usable recovery proof or the alert posture is not configured

## 5. Security Hardening Checks

- confirm `APP_DEBUG=false` in production
- confirm `/docs` and `/redoc` are disabled in production
- confirm all default secrets are replaced
- confirm the API rate limits the most sensitive auth flows
- confirm internal services are not exposed on public ports

## 6. Upgrade Notes

- The preferred upgrade path is `bash scripts/deploy_release.sh upgrade`.
- That helper runs preflight checks, captures a backup, rebuilds the stack, applies Alembic migrations, and reruns the smoke check.
- Capture backup evidence before applying a schema change.
- Re-run the smoke check after every upgrade or rollback.

## 7. Real Full-Stack Release Gate (S128)

Before a controlled pilot or promotion, run the deterministic production-like gate
(PostgreSQL, Redis, API, Celery worker with embedded beat, Vue/PWA, seeded COMBIS
and Tenant X):

```bash
KAIRO_GATE_BASE_URL=http://localhost:8080 node scripts/run-full-stack-gate.mjs
cd apps/web && KAIRO_GATE_BASE_URL=http://localhost:8080 npm run test:e2e:real
```

Expected outcome (validated 2026-10-03):

- 30/30 API/worker scenario steps pass: finance lifecycle, domain event → outbox
  → worker → inbox, deep-link contract, installation registration/revocation,
  branding, manifest, host resolution, tenant isolation and role authorization.
- 3/3 real browser tests pass: branding/manifest, single Service Worker, WCAG 2.2
  AA, exact deep-link route, offline shell, FR/EN/DE, Android viewport, sign-out.

Full commands: `docs/operations/deployment-runbook.md` §8. Automated evidence and
the pending manual Chrome Android steps:
`docs/pwa/COMBIS_PILOT_CHECKLIST.md`.

### Known limitations of the gate

- MinIO is operator-provisioned (public images require registry authentication
  since 2025); the validated scenario does not upload documents.
- The GitHub workflow is configured but has not yet executed in GitHub Actions.
- Real-device validation (closed-app push, system-notification deep link,
  on-device revocation, application update) has no automated equivalent and stays
  explicitly pending until the operator records it.
- The historical `JWT_SECRET_KEY` exposure in commit `2f03643f` remains a
  HUMAN_REQUIRED rotation/remediation item; HEAD fails closed without an operator
  secret.

## Evidence To Record

- compose config output
- build logs
- restore drill summary
- tenant recovery evidence record
- `/health` output
- `/metrics` output
- Grafana screenshot or Prometheus target status if the optional monitoring package is enabled
- any deviations or known gaps
