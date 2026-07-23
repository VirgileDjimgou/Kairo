# Validation Baseline

Last updated: 2026-07-22

This document captures the active quality-gate commands that are expected to work from the repository root unless noted otherwise.

## Backend

Run the full backend suite from the repository root:

```bash
python -m pytest services/api/tests -q
```

Run the full Ruff baseline covering all backend modules:

```bash
python -m ruff check services/api/app/ services/api/tests/ --ignore E501
```

Run the full Mypy baseline covering all backend modules:

```bash
python -m mypy --config-file services/api/pyproject.toml --explicit-package-bases \
  services/api/app/
```

Notes:

- The backend test suite defaults to an isolated SQLite database when `TEST_DATABASE_URL` is not set to PostgreSQL.
- 264 integration tests pass (latest verified count).
- Ruff baseline covers the entire `app/` tree and all tests with `--ignore E501` to focus on meaningful rules (security, unused imports, error handling) without cosmetic line-length noise.
- Mypy baseline now covers all 151 source files across the entire `app/` tree — all modules, providers, core, db, and main.py — with zero errors.

## Frontend

Run the frontend type check:

```bash
cd apps/web
npm run type-check
```

Run the production build:

```bash
cd apps/web
npm run build
```

Run the selected browser regression pack:

```bash
cd apps/web
npm run test:e2e:locale
```

Run the role-security browser subset:

```bash
cd apps/web
npm run test:e2e:roles
```

Run the release-candidate browser matrix:

```bash
cd apps/web
npm run test:e2e:release-candidate
```

Run the release-candidate backend matrix:

```bash
python -m pytest services/api/tests/test_release_candidate_matrix.py -q
```

Run the production gateway smoke check after starting the production Compose stack:

```powershell
.\scripts\production_smoke.ps1 -BaseUrl http://localhost
```

Run the non-disclosing operational pilot preflight before using a real domain or tunnel:

```powershell
.\scripts\pilot_acceptance_preflight.ps1 -EnvFile .env
```

Launch a temporary Quick Tunnel demonstration without changing `.env`:

```powershell
.\scripts\start_quick_demo.ps1
```

Validate a workbook import without changing data:

```powershell
docker compose exec -T api python -m app.db.import_members_workbook `
  --workbook /tmp/kairo-member-import.xlsx `
  --credentials-output /app/.private/member-imports/dry-run.csv
```

Validate the named production tunnel after the Cloudflare token is set:

```powershell
.\scripts\pilot_acceptance_preflight.ps1 -EnvFile .env.production.local
.\scripts\production_smoke.ps1 -BaseUrl https://app.combissportverein.org
```

Notes:

- `apps/web/playwright.config.ts` now selects `npm.cmd` on Windows and `npm` elsewhere so the same Playwright suite can run locally and in Linux CI.
- The localization pack is the current browser baseline because it exercises the FR-first contract, authenticated session bootstrapping, principal-admin admin surfaces, and the role-scoped workspaces most affected by recent changes.
- The role-authorization matrix is a CI gate. It proves member self-finance isolation and tenant-token renewal, plus direct finance-route denials for secretary general, auditor, censor, and sports manager without requiring a live backend. Latest verified result: 14 Chromium tests passed.
- The release-candidate browser matrix is a CI gate for the nine target roles. It verifies role-specific landing workspaces, sidebar entry points, and configured direct-route denials. Latest verified result: 9 Chromium tests passed.
- The release-candidate backend matrix runs against isolated SQLite and is included in the full backend CI suite. Latest verified result: 2 tests passed.
- The PowerShell smoke check mirrors the Bash production gate for Windows operators: root, health, metrics, and the public blocking of `/docs`, `/redoc`, and `/openapi.json`.
- The pilot preflight reports only pass/fail requirements for production mode, non-placeholder secrets, HTTPS, CORS, and a Cloudflare Tunnel token. It never prints secret values.
- The Quick Tunnel helper is demonstration-only. It writes an ignored `.env.quick-demo`, exposes only web and API endpoints, and restores the standard local web/API environment through `./scripts/stop_quick_demo.ps1`.
- The controlled member import runs only from `scripts/import_real_members.ps1`; it blocks active Quick Tunnels, makes a private database dump, and preserves all non-member-only tenant data.
- The named production tunnel uses the same-origin `app.combissportverein.org` hostname. Rotate the existing local PostgreSQL password through `scripts/activate_production_database_credentials.ps1` only after the production environment is generated and before the first production Compose start.
- `vue-tsc` runs with `strict`, `exactOptionalPropertyTypes`, and `noUncheckedIndexedAccess`, so optional API fields and list access must be handled explicitly.
