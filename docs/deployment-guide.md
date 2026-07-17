# Kairo Deployment Guide

This guide covers production deployment and remote exposure via Cloudflare Tunnel.

For the shortest install, upgrade, and rollback workflow, pair this guide with [`docs/operations/deployment-runbook.md`](./operations/deployment-runbook.md).

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Production Build](#production-build)
- [Environment Configuration](#environment-configuration)
- [Reverse Proxy (Caddy)](#reverse-proxy-caddy)
- [Cloudflare Tunnel](#cloudflare-tunnel)
- [Backup and Restore](#backup-and-restore)
- [Production Validation](#production-validation)
- [Security Checklist](#security-checklist)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
Internet
  │
  ▼
Cloudflare Edge  (TLS termination, DDoS protection)
  │
  ▼
cloudflared tunnel  (runs on your machine, outbound only — no open ports)
  │
  ▼
Reverse proxy (Caddy or Nginx)  —  optional, simplifies routing
  ├── /         → frontend static files
  └── /api/*    → FastAPI backend
  │
  ├── web container     (Nginx, port 80)
  ├── api container     (FastAPI, port 8000)
  ├── worker container  (Celery)
  ├── postgres          (port 5432 — private)
  ├── redis             (port 6379 — private)
  ├── qdrant            (port 6333 — private)
  ├── minio             (port 9000 — private)
  └── ollama            (port 11434 — private)
```

**Key principle:** Only the web and API services are exposed. All databases, queues, and internal services remain on the internal Docker network.

---

## Prerequisites

- Docker and Docker Compose (v2+)
- A domain managed by Cloudflare
- Cloudflare Zero Trust account (free tier works)

---

## Production Build

### 1. Clone and configure

```bash
git clone <repository-url> kairo
cd kairo
cp .env.production.example .env
# Edit .env — change all secrets
bash scripts/deploy_release.sh preflight
```

### 2. Build and start

```bash
# First production install
bash scripts/deploy_release.sh install
```

### 3. Verify

```bash
# Built-in smoke validation
bash scripts/production_smoke.sh
```

---

## Environment Configuration

### Essential variables to change in production

| Variable | Why |
|----------|-----|
| `JWT_SECRET_KEY` | Generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `POSTGRES_PASSWORD` | Database access credential |
| `MINIO_ROOT_PASSWORD` | Object storage credential |
| `CORS_ORIGINS` | Must include the exact origin the browser sees (e.g., `https://orgmind.yourdomain.com`) |

### Frontend API URL

The frontend Vite build embeds `VITE_API_BASE_URL`. For production:

- **Same-origin proxy (recommended):** set `VITE_API_BASE_URL=/api/v1`
- **Separate subdomain:** set `VITE_API_BASE_URL=https://api.orgmind.yourdomain.com/api/v1`

---

## Reverse Proxy (Caddy)

Using a reverse proxy simplifies routing and provides a single port for Cloudflare Tunnel.

### With Docker Compose

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
               -f infra/reverse-proxy/docker-compose.caddy.yml up -d
```

### Without Docker

Install Caddy and use `infra/reverse-proxy/Caddyfile` as a starting point.

### Caddyfile overview

The provided Caddyfile (`infra/reverse-proxy/Caddyfile`) handles:

- Static file serving for the Vue SPA with SPA fallback
- API reverse proxy to the FastAPI backend
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Blocking of `/docs` and `/redoc` in production
- Automatic Let's Encrypt TLS (when a domain is configured)

---

## Cloudflare Tunnel

Cloudflare Tunnel creates an encrypted outbound-only connection from your machine to Cloudflare's edge. No open firewall ports needed.

### Option A: Docker (recommended)

1. Go to [Cloudflare Zero Trust](https://dash.cloudflare.com/) → Networks → Tunnels
2. Create a tunnel and copy the token
3. Set `CLOUDFLARE_TUNNEL_TOKEN=your-token` in `.env`
4. Start the tunnel:
   ```bash
   docker compose --profile tunnel up -d
   ```

### Option B: Standalone cloudflared

1. Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install/
2. Authenticate: `cloudflared tunnel login`
3. Create a tunnel: `cloudflared tunnel create kairo-local`
4. Copy the generated credentials file to `~/.cloudflared/`
5. Edit `infra/cloudflare/config.yml.example` and save as `~/.cloudflared/config.yml`
6. Run the tunnel:
   ```bash
   cloudflared tunnel --config ~/.cloudflared/config.yml run
   ```

### DNS Configuration

In your Cloudflare dashboard, add a CNAME record pointing your domain to the tunnel:

| Type | Name | Target |
|------|------|--------|
| CNAME | orgmind | `<tunnel-id>.cfargotunnel.com` |

### Tunnel Ingress Rules

The cloudflare config sample (`infra/cloudflare/config.yml.example`) shows:

- **Single domain with reverse proxy:** Route to `localhost:80` (Caddy/Nginx handles / and /api/*)
- **Separate subdomains:** Route `app.yourdomain.com` → `localhost:80` and `api.yourdomain.com` → `localhost:8000`

---

## Backup and Restore

### Automated backup

```bash
bash scripts/backup.sh              # creates ./backups/kairo-backup-<timestamp>.tar.gz
bash scripts/backup.sh /mnt/backups # custom directory
```

The script backs up all persistent data:

| Service | Data | Format |
|---------|------|--------|
| PostgreSQL | All databases | SQL dump |
| Redis | In-memory state | RDB snapshot |
| Qdrant | Vector embeddings | Storage directory |
| MinIO | Uploaded files | Data directory |
| Ollama | Downloaded models | Model files |

### Automated restore

```bash
bash scripts/restore.sh ./backups/kairo-backup-20260629_120000.tar.gz
```

The restore script:
1. Extracts the backup archive
2. Restores PostgreSQL from the SQL dump
3. Restores Redis RDB, Qdrant storage, MinIO data, and Ollama models
4. Restarts affected services so they pick up the restored data
5. Cleans up temporary files

After restore, run the production smoke check to verify:

```bash
bash scripts/production_smoke.sh
```

### Guided install, upgrade, and rollback

Use the release helpers for the full production path:

```bash
# Preflight only
bash scripts/deploy_release.sh preflight

# First install
bash scripts/deploy_release.sh install

# Upgrade with automatic backup + smoke validation
bash scripts/deploy_release.sh upgrade

# Roll back to a known-good backup
bash scripts/rollback_release.sh ./backups/kairo-backup-YYYYMMDD_HHMMSS.tar.gz
```

### Manual restore (alternative)

If the automated script is unavailable, follow these steps:

```bash
# 1. Stop all containers
docker compose down

# 2. Restore from backup
tar -xzf path/to/backup.tar.gz -C /tmp/restore

# 3. Restore PostgreSQL
docker compose up -d postgres
docker compose exec -T postgres psql -U orgmind < /tmp/restore/postgres.sql

# 4. Restore Qdrant
docker compose up -d qdrant
docker cp /tmp/restore/qdrant_storage $(docker compose ps -q qdrant):/qdrant/storage

# 5. Restore MinIO
docker compose up -d minio
docker cp /tmp/restore/minio_data $(docker compose ps -q minio):/data

# 6. Restore Redis (if needed)
docker compose up -d redis
docker cp /tmp/restore/redis.rdb $(docker compose ps -q redis):/data/dump.rdb
docker compose restart redis

# 7. Restore Ollama (if needed)
docker compose up -d ollama
docker cp /tmp/restore/ollama_data $(docker compose ps -q ollama):/root/.ollama
docker compose restart ollama

# 8. Start all services
docker compose up -d
```

### Scheduling backups (cron)

```bash
# Daily backup at 3 AM
0 3 * * * bash /path/to/kairo/scripts/backup.sh /mnt/backups >> /var/log/kairo-backup.log 2>&1
```

---

## Production Validation

For a repeatable production smoke check, use:

```bash
bash scripts/production_smoke.sh http://localhost
```

For the full validation and restore workflow, see [`docs/operations/production-readiness.md`](docs/operations/production-readiness.md) and [`docs/operations/deployment-runbook.md`](./operations/deployment-runbook.md).

For customer-facing packaging and go-live preparation, see:

- [`docs/commercial/README.md`](docs/commercial/README.md)
- [`docs/commercial/demo-to-production-checklist.md`](docs/commercial/demo-to-production-checklist.md)
- [`docs/commercial/support-playbook.md`](docs/commercial/support-playbook.md)

---

## Security Checklist

### Before going live

- [ ] Changed all default passwords (`JWT_SECRET_KEY`, `POSTGRES_PASSWORD`, `MINIO_ROOT_PASSWORD`)
- [ ] Set `APP_DEBUG=false` and `APP_ENV=production`
- [ ] API docs disabled automatically when `APP_DEBUG=false`
- [ ] `bash scripts/deploy_release.sh preflight` passes
- [ ] CORS origins match your actual domain(s)
- [ ] Cloudflare Tunnel configured — no ports exposed on the public internet
- [ ] Internal service ports (5432, 6379, 6333, 9000, 9001, 11434) are NOT exposed through the tunnel
- [ ] Backups configured and tested
- [ ] `.env` file added to `.gitignore` (already present by default)
- [ ] No secrets committed to the repository

### During operation

- Rotate `JWT_SECRET_KEY` periodically
- Monitor Docker logs: `docker compose logs --tail=100 -f`
- Check backup integrity monthly
- Re-run `bash scripts/production_smoke.sh` after every upgrade or rollback
- Keep Cloudflare Access (Zero Trust) in mind for admin route protection

---

## Troubleshooting

### Frontend shows blank page

- Check `VITE_API_BASE_URL` — it must match the production URL
- Verify the nginx/Caddy config has proper SPA fallback (`try_files $uri $uri/ /index.html`)
- Clear browser cache (Vite assets are cached aggressively)

### API returns CORS errors

- Verify `CORS_ORIGINS` in `.env` matches the exact origin (with protocol and port if any)
- If using a reverse proxy, ensure `X-Forwarded-*` headers are passed correctly

### Cloudflare Tunnel not connecting

- Verify `CLOUDFLARE_TUNNEL_TOKEN` is set correctly
- Check cloudflared logs: `docker compose logs cloudflared`
- Run without Docker to debug: `cloudflared tunnel --no-autoupdate run --token <token>`
- Ensure outbound connectivity to `api.cloudflare.com` (no corporate firewall blocking)

### Backup script fails

- Ensure `docker compose` is available and the project is running
- Set `COMPOSE_PROJECT` if using a non-default project name:
  ```bash
  COMPOSE_PROJECT=myproject bash ./scripts/backup.sh
  ```

### Worker not processing jobs

- Check Redis is reachable: `docker compose logs redis`
- Check worker logs: `docker compose logs worker`
- Verify `REDIS_URL` and `INGESTION_AUTO_ENQUEUE=true`
