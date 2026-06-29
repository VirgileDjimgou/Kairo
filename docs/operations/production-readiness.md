# Production Readiness And Recovery

This document captures the validation steps for Sprint 24.

## 1. Production Build Validation

Run from the repository root:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
docker compose -f docker-compose.yml -f docker-compose.prod.yml build api web
```

Expected outcome:

- compose config renders without errors
- both production images build successfully
- the API container starts with production settings
- the web container serves the built SPA through nginx

## 2. Production Smoke Check

Once the stack is running:

```bash
curl http://localhost/health
curl http://localhost/metrics
curl http://localhost/
```

Expected outcome:

- `/health` reports dependency status and module list
- `/metrics` returns runtime metrics text
- `/` serves the SPA entry point

## 3. Backup And Restore Drill

Create a backup:

```bash
chmod +x scripts/backup.sh
./scripts/backup.sh ./backups
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

## 4. Security Hardening Checks

- confirm `APP_DEBUG=false` in production
- confirm `/docs` and `/redoc` are disabled in production
- confirm all default secrets are replaced
- confirm the API rate limits the most sensitive auth flows
- confirm internal services are not exposed on public ports

## 5. Upgrade Notes

- Always run Alembic migrations before starting the new release.
- Capture backup evidence before applying a schema change.
- Re-run the smoke check after every upgrade.

## Evidence To Record

- compose config output
- build logs
- restore drill summary
- `/health` output
- `/metrics` output
- any deviations or known gaps
