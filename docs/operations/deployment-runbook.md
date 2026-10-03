# Kairo Deployment Runbook

This runbook is the shortest operator path for a self-hosted production deployment.

## 1. Prepare the environment

```bash
cp .env.production.example .env
# Edit .env and replace every placeholder secret.
```

Recommended minimum checks before the first install or an upgrade:

```bash
bash scripts/deploy_release.sh preflight
```

This verifies:

- `.env` exists and is production-oriented
- critical secrets are no longer placeholders
- the production Compose configuration renders successfully

## 2. First installation

```bash
bash scripts/deploy_release.sh install
```

Optional demo seeding immediately after installation:

```bash
KAIRO_RUN_DEMO_SEED=1 bash scripts/deploy_release.sh install
```

## 3. Routine upgrade

```bash
bash scripts/deploy_release.sh upgrade
```

The upgrade helper:

1. runs the same preflight checks
2. creates a backup archive (`scripts/backup.sh`, infrastructure level)
3. rebuilds the production images
4. starts the production stack
5. applies Alembic migrations
6. runs the smoke check

If you intentionally already captured a backup, you can skip the automatic one:

```bash
KAIRO_SKIP_BACKUP=1 bash scripts/deploy_release.sh upgrade
```

Always keep the pre-migration backup. The application-level encrypted backup CLI
(`Backup-Kairo.ps1` / `backup` command) runs the new code and therefore cannot be
used before migrations have been applied to an older database; the
infrastructure backup is the supported safety path.

Verify the upgrade before declaring it complete:

```bash
docker compose exec -T api alembic current          # must equal the release head
curl -fsS http://localhost/health | jq .            # database/backup/outbox ok
```

For the current release head, `0033`, the expected post-upgrade state and the
validated data-preservation checklist are recorded in
`docs/sprint-118-release-candidate-evidence.md`.

## 4. Rollback

Rollback requires a backup archive produced by `scripts/backup.sh` or by the upgrade helper.

```bash
bash scripts/rollback_release.sh ./backups/kairo-backup-YYYYMMDD_HHMMSS.tar.gz
```

The rollback helper restores PostgreSQL, Redis, Qdrant, MinIO, and Ollama data, restarts the application services, then re-runs the smoke check.

The restore/rollback path is rehearsed without touching production data:

```powershell
# Windows workstation: verify and restore an encrypted archive into a disposable container
.\scripts\Test-KairoRecoveryDrill.ps1 -ArchiveName "<archive>.enc" -EnvironmentFile .env.core
```

```bash
# Linux host backup/restore pair
bash scripts/backup.sh /mnt/backups
bash scripts/restore.sh /mnt/backups/kairo-backup-YYYYMMDD_HHMMSS.tar.gz
```

A rollback is complete only after the smoke check passes and the restored
database reports the expected Alembic revision:

```bash
docker compose exec -T api alembic current
```

## 5. Smoke validation only

```bash
bash scripts/production_smoke.sh
```

Override the public URL when needed:

```bash
bash scripts/production_smoke.sh https://kairo.example.com
```

## 6. Manual backup

```bash
bash scripts/backup.sh
```

Custom backup directory:

```bash
bash scripts/backup.sh /mnt/backups
```

## 7. Recovery evidence

After every real backup, restore drill, upgrade, or rollback, update the tenant recovery evidence in the product so the admin health center reflects the latest operational truth.

## 8. Real full-stack release gate (S128)

Before promoting a release candidate, run the deterministic production-like gate
against seeded COMBIS and Tenant X data. It exercises the real path browser → Vue
→ nginx → FastAPI → PostgreSQL → domain event → notification outbox → Celery
worker → authenticated inbox → deep link → authorized route, with no API mocking:

```bash
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  up -d postgres redis
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  run --rm api alembic upgrade head
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  run --rm api python /app/scripts/seed_full_stack.py
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  up -d api worker web

KAIRO_GATE_BASE_URL=http://localhost:8080 node scripts/run-full-stack-gate.mjs
cd apps/web && KAIRO_GATE_BASE_URL=http://localhost:8080 npm run test:e2e:real
```

`docker-compose.release-gate.yml` runs Celery with an embedded beat (so the
outbox drains automatically), publishes web/API ports for the browser gate
(`KAIRO_GATE_WEB_PORT`/`KAIRO_GATE_API_PORT`) and sets `PLATFORM_BASE_DOMAIN` for
host-resolution checks. `docker-compose.ci.yml` excludes MinIO because MinIO
public images are operator-provisioned since 2025. The workflow
`.github/workflows/full-stack-release-gate.yml` runs the same steps manually or
nightly with evidence upload; the automated and manual results are tracked in
`docs/pwa/COMBIS_PILOT_CHECKLIST.md`.
