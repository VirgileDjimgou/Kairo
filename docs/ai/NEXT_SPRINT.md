# Next Sprint

## Last Completed Sprint

Sprint 35 - Operational Reliability, Data Safety, And Migration Discipline

Status: Completed

## What Was Delivered In Sprint 35

### Operational scripts
- `scripts/restore.sh` — automated full restore from backup archives (PostgreSQL, Redis, Qdrant, MinIO, Ollama)
- `scripts/production_smoke.sh` — now validates response body content (health status field, metrics HELP prefix), checks /docs and /redoc redirects, reports pass/fail per check

### Docker healthchecks
- `api` service — `curl -sf http://localhost:8000/health`
- `worker` service — `pgrep -f 'celery.*worker'`
- `web` service — Node.js built-in TCP port check against port 5173

### Migration chain gap fixes
- **0009_user_sessions** — creates the `user_sessions` table (Sprint 32 model was never migrated; only existed via `Base.metadata.create_all()` in tests)
- **0010_document_version_fk** — adds missing FK constraint on `documents.current_version_id` → `document_versions.id`
- Fixed `contributions/models.py` — `Numeric(12, 2)` precision annotations now match the 0006 migration

### Tests & bug fixes
- 8 new health endpoint tests covering response shape, per-service status/latency, and Prometheus metrics format
- Fixed pre-existing `test_audit_trail_is_tenant_scoped` failure (login audit events recorded during test setup polluted the assertion)
- 171 backend tests pass, 0 failures

### Documentation
- Deployment guide updated: "Backup and Restore" section now references `scripts/restore.sh` as the primary restore path

## Sprint 35 Closed

- Sprint 35 is complete.
- The next official sprint is now `Sprint 36 - Association Operations Robustness`.

## Handoff Guidance

- Read `constitution/KAIRO_CONSTITUTION.md`
- Read `IMPLEMENTATION_ROADMAP.md`
- Read `PROJECT_STATUS.md`
- Read `prompts/CODEX_AUTOPILOT.md`
- Next official sprint: `Sprint 36 - Association Operations Robustness`
- Final stabilization target: `Sprint 37 - Final Open-Source Release Stabilization And Portfolio Readiness`

## Notes

- Do not continue from memory alone.
- All changes are uncommitted.
- The current objective is a stable open-source release suitable for a portfolio and for an organization of about 200 members.
