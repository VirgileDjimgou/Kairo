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
2. creates a backup archive
3. rebuilds the production images
4. starts the production stack
5. applies Alembic migrations
6. runs the smoke check

If you intentionally already captured a backup, you can skip the automatic one:

```bash
KAIRO_SKIP_BACKUP=1 bash scripts/deploy_release.sh upgrade
```

## 4. Rollback

Rollback requires a backup archive produced by `scripts/backup.sh` or by the upgrade helper.

```bash
bash scripts/rollback_release.sh ./backups/kairo-backup-YYYYMMDD_HHMMSS.tar.gz
```

The rollback helper restores PostgreSQL, Redis, Qdrant, MinIO, and Ollama data, restarts the application services, then re-runs the smoke check.

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
