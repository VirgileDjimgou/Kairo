# Kairo Portfolio Deployment Runbook

This runbook operates only the Kairo Web/PWA core at
`https://kairo.patrickdjimgou.dev`. It does not manage Fabrik3D.

## Production layout

- Host path: `/home/kairo/kairo-release`
- Compose project: `kairo`
- Compose file: `docker-compose.core.yml`
- Environment file: `.env.core` (mode `0600`, never committed)
- Public ingress: the dedicated Cloudflare tunnel `kairo-portfolio` to `http://web:80`

The compose file has no host-published application ports. PostgreSQL, Redis,
MinIO and all application containers remain private to the Kairo Docker network.

## Initial release

1. Upload or check out an immutable Git revision to `/home/kairo/kairo-release`.
2. Generate production-only values in `.env.core`; set `APP_BASE_URL` and
   `CORS_ORIGINS` to `https://kairo.patrickdjimgou.dev`.
3. Create the `kairo-portfolio` Cloudflare tunnel and configure the single
   public hostname `kairo.patrickdjimgou.dev` with service `http://web:80`.
4. Run `KAIRO_CORE_ENV_FILE=/home/kairo/shared/.env.core bash scripts/deploy_core_release.sh install`.
5. Confirm the six smoke checks, then validate the login and mobile PWA install.

## Routine update

1. Record the currently deployed revision and fetch the chosen new revision.
2. Run `KAIRO_CORE_ENV_FILE=/home/kairo/shared/.env.core bash scripts/deploy_core_release.sh upgrade`.
3. The helper creates a PostgreSQL, Redis and MinIO backup archive before it
   rebuilds containers, runs Alembic migrations explicitly, starts only Kairo,
   and executes the public smoke check.
4. Record the resulting revision, migration revision and archive path.

Never use an unscoped `docker compose down`, prune command, or an operation in
the Fabrik3D directory while managing Kairo.

## Rollback rule

For a code-only failure, restore the previously recorded Git revision and run
the `upgrade` command after taking a new safety backup. For a schema migration
failure, restore PostgreSQL and MinIO from the pre-upgrade archive in an
isolated recovery procedure before restarting Kairo. Do not attempt a database
rollback by guessing migration commands.
