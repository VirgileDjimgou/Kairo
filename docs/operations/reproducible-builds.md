# Reproducible Builds And CI Pipeline

Status: Active — Roadmap V2 Sprint 127
Related: ADR-014 (Flutter freeze), `docs/operations/validation-baseline.md`

The default `main` pipeline is **Security → API → Contracts → Web →
Production**. Flutter is not a blocking job (ADR-014); it runs through the
manual `Flutter Legacy Reference` workflow.

## Security job

1. `node scripts/check-sensitive-files.mjs` rejects databases, backups,
   operational documents, member/finance exports and secret-bearing files.
2. Repository guards run next: API collection paths, FR/EN/DE catalog parity,
   capability bundles, canonical PWA Service Worker.
3. `gitleaks` scans the full history for secrets **after** the guards.

Runtime evidence (screenshots, XML/JSON dumps, Playwright reports, test videos,
device captures) is never committed: `.gitignore` excludes `artifacts/`,
`apps/web/artifacts/`, `apps/web/playwright-report/` and
`apps/web/test-results/`, and the Web job uploads them as workflow artifacts
instead.

## API job

- Installs `tesseract-ocr` with `eng`, `fra` and `deu` language data so the OCR
  tests run and pass; the tests are never skipped in CI.
- Installs Python dependencies with `requirements.txt` constrained by
  `services/api/requirements.lock` (123 exact pins generated on
  `python:3.12-slim`), so resolution is deterministic.
- Runs `ruff`, `mypy` and the full backend suite.

## Contracts job

- Asserts `export_openapi.py` emits pure machine-readable JSON (no logging
  pollution).
- Detects breaking OpenAPI changes against the committed baseline.
- Verifies generated **TypeScript** contracts are current
  (`generate-client-contracts.mjs --check --typescript-only`). The frozen Dart
  contracts are checked only in the manual Flutter workflow, so Flutter can
  never block the release pipeline.
- Verifies every literal client call maps to a documented operation.

## Web job

`npm ci` against the committed `package-lock.json`, type-check, i18n coverage
report, production build, and all Chromium packs (locale, roles,
release-candidate, accessibility, PWA dev + built, notification installations,
white-label/domains). Evidence is uploaded as `web-browser-evidence`.

## Production job

1. Builds the real production images (`api`, `web`) with pinned base images and
   the locked Python dependencies.
2. Starts PostgreSQL and Redis, then applies the full Alembic chain
   (`alembic upgrade head`) against real PostgreSQL.
3. Starts the production API and web containers and waits for
   `/health/ready`.
4. Verifies `/health/live`, `/health/ready` and that nginx serves the built web
   shell.
5. Tears down with volumes.

`docker-compose.ci.yml` is a CI-only override: MinIO's public images moved behind
registry authentication in 2025, so the smoke job verifies API, web, PostgreSQL
and Redis while MinIO/S3 stays an operator-provisioned dependency.

## Image and dependency pinning

| Component | Pin |
| --- | --- |
| API base image | `python:3.12-slim@sha256:dddfd7e0…` (builder, development, production) |
| Web build/dev base | `node:20-alpine@sha256:fb4cd12c…` |
| Web serve | `nginx:1.27-alpine@sha256:65645c7b…` |
| PostgreSQL | `postgres:16-alpine@sha256:721873c3…` |
| Redis | `redis:7-alpine@sha256:858f009f…` |
| Qdrant | `qdrant/qdrant:v1.19.1` |
| Ollama | `ollama/ollama:0.35.1` |
| Cloudflared | `cloudflare/cloudflared:2026.9.3` |
| MinIO | `quay.io/minio/minio:RELEASE.2024-06-13T22-53-53Z` (registry credentials required) |
| Python | `services/api/requirements.lock` (exact pins) |
| Node | `apps/web/package-lock.json` + `npm ci` |

`.dockerignore` files keep secrets (`.private/`, `.env*`), local databases,
logs, caches and test output out of build contexts.
