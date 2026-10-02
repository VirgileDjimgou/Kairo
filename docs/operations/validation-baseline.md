# Validation Baseline

Last updated: 2026-10-03

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
- 362 integration tests pass (latest verified count, 2026-09-27; includes the three notification-recovery tests added in Sprint 118).
- Ruff baseline covers the entire `app/` tree and all tests with `--ignore E501` to focus on meaningful rules (security, unused imports, error handling) without cosmetic line-length noise.
- Mypy baseline now covers all 301 source files across the entire `app/` tree — all modules, providers, core, db, and main.py — with zero errors.

## Frontend

Guard the canonical FastAPI collection routes used by the web client (prevents the
slash-less redirect that breaks HTTPS surfaces):

```bash
node scripts/check-api-collection-paths.mjs
```

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

Run the accessibility audit pack (axe-core, WCAG 2.2 AA tags):

```bash
cd apps/web
npm run test:e2e:a11y
```

- The pack scans the public login at 320 px and desktop widths, the authenticated
  shell at phone and desktop widths, the skip link, visible focus and reduced
  motion. `@axe-core/playwright` is a web dev dependency. Audit record:
  `docs/operations/accessibility-audit.md`.
- Latest verified result: 6 Chromium tests passed.

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
- The Playwright suite runs on the dedicated port `5273` (override with `PLAYWRIGHT_WEB_PORT`) because the Compose stack publishes `5173` (web) and `8000` (api); reusing those ports silently pointed the browser tests at a containerised build instead of the working tree. A global warm-up navigation compiles the Vite graph before the first test so a cold server cannot eat assertion timeouts.
- The localization pack is the current browser baseline because it exercises the FR-first contract, authenticated session bootstrapping, principal-admin admin surfaces, and the role-scoped workspaces most affected by recent changes.
- The role-authorization matrix is a CI gate. It proves member self-finance isolation and tenant-token renewal, plus direct finance-route denials for secretary general, auditor, censor, and sports manager without requiring a live backend. Latest verified result: 17 Chromium tests passed.
- The release-candidate browser matrix is a CI gate for the nine target roles. It verifies role-specific landing workspaces, sidebar entry points, and configured direct-route denials. Latest verified result: 9 Chromium tests passed.
- The release-candidate backend matrix runs against isolated SQLite and is included in the full backend CI suite. Latest verified result: 2 tests passed.
- The PowerShell smoke check mirrors the Bash production gate for Windows operators: root, health, metrics, and the public blocking of `/docs`, `/redoc`, and `/openapi.json`.
- The pilot preflight reports only pass/fail requirements for production mode, non-placeholder secrets, HTTPS, CORS, and a Cloudflare Tunnel token. It never prints secret values.
- The Quick Tunnel helper is demonstration-only. It writes an ignored `.env.quick-demo`, exposes only web and API endpoints, and restores the standard local web/API environment through `./scripts/stop_quick_demo.ps1`.
- The controlled member import runs only from `scripts/import_real_members.ps1`; it blocks active Quick Tunnels, makes a private database dump, and preserves all non-member-only tenant data.
- The named production tunnel uses the same-origin `app.combissportverein.org` hostname. Rotate the existing local PostgreSQL password through `scripts/activate_production_database_credentials.ps1` only after the production environment is generated and before the first production Compose start.
- `vue-tsc` runs with `strict`, `exactOptionalPropertyTypes`, and `noUncheckedIndexedAccess`, so optional API fields and list access must be handled explicitly.

## Flutter (frozen reference — optional/manual)

Flutter is **FROZEN / LEGACY REFERENCE** (ADR-014, Sprint 119). It is not part of
the default blocking pipeline; a Flutter failure cannot make `main` red.

```powershell
# Optional, manual: run the "Flutter Legacy Reference" GitHub workflow instead.
Set-Location apps/flutter_kairo
.\scripts\flutter.ps1 analyze
.\scripts\flutter.ps1 test
Set-Location ../..
```

- The generated Dart contract drift check and the Flutter route-coverage scan
  remain in the blocking Contracts job because they are deterministic, SDK-free
  checks of the API boundary (`npm run contracts:check`).
- Capability continuity and deprecations: `docs/pwa/FLUTTER_TO_PWA_PARITY.md`.

## Notification Operations

```bash
npm run notifications:firebase:doctor
npm run notifications:firebase:doctor -- --json
```

- The doctor prints only non-secret diagnostics (environment presence, credential
  file presence, project id, Python packages). Nothing is sent unless `--live` is
  passed with `FIREBASE_TEST_TOKEN`; it never runs in generic CI.
- Event matrix and operator guide: `docs/notifications/NOTIFICATION_EVENT_MATRIX.md`
  and `docs/notifications/NOTIFICATION_OPERATOR_GUIDE.md`.

## Performance

```bash
npm run perf:baseline
npm run perf:check
```

- The harness seeds deterministic 200- and 1000-member tenants with three years
  of finance history and records p50/p95 latency plus SQL statement counts for
  representative operations in `docs/performance/performance-baseline.json` and
  `docs/performance/PERFORMANCE_BASELINE.md` (ADR-012).
- `perf:check` reruns the 200-member workload and fails when p95 or statement
  counts exceed committed thresholds. It is opt-in (not generic CI) because
  absolute latency depends on the machine; statement counts are deterministic.

## Contracts

```bash
npm run contracts:check
node scripts/check-openapi-contract.mjs        # breaking-change detector
node scripts/check-openapi-contract.mjs --update
node scripts/generate-client-contracts.mjs     # regenerate TS + Dart contracts
node scripts/generate-client-contracts.mjs --check
node scripts/check-client-route-coverage.mjs
```

- `docs/api/openapi.json` is the committed schema; `services/api/scripts/export_openapi.py`
  generates it deterministically.
- Breaking changes (removed operations/parameters/response fields, newly required
  request fields, type changes, enum removals) fail CI; additive changes are
  reported. Refresh intentionally with `npm run openapi:update`.
- Generated clients: `apps/web/src/api/generated/contracts.ts` and
  `apps/flutter_kairo/lib/core/api/generated/contracts.dart`; the drift check
  fails when either file is stale.
- Route coverage validates 151 Vue calls and 42 literal Flutter calls, and reports
  the remaining dynamic Flutter dispatchers. Matrix:
  `docs/api/CLIENT_FEATURE_PARITY.md`; decision: ADR-011.

## Repository Guards

```bash
node scripts/check-sensitive-files.mjs
node scripts/check-i18n-parity.mjs
node scripts/check-i18n-coverage.mjs
node scripts/check-api-collection-paths.mjs
node scripts/check-capability-bundles.mjs
```

- The capability-bundle guard regenerates the web fallback map from the backend role catalog and fails when
  `apps/web/src/config/capabilityBundles.ts` drifts. Verified 2026-09-26: bundles match and the API exposes
  capabilities on `/auth/me` and tenant memberships (ADR-008).

- The i18n parity guard compares every feature catalog under `apps/web/src/i18n/{fr,en,de}` and fails when a locale is missing a catalog file, a key, or a value. Verified 2026-09-26: 11 feature catalogs, 873 keys per locale, exact parity.

- The sensitive-file scanner rejects database files, backup/dump archives, spreadsheet workbooks, operational documents (PDF/DOCX/DOC/ODT/PPTX/RTF), tabular exports (CSV/TSV outside the fictional `seed/` fixtures), member/finance exports and secret-bearing key material. Source directories named `backup` or `export` are correctly ignored (they are module code, not archives), and the member/finance data-export rule skips source trees (`apps/web/src/`, `apps/flutter_kairo/lib/`, `services/api/app/`) so JSON catalogs such as `apps/web/src/i18n/fr/membership.json` are treated as code. Verified 2026-09-26: 1144 tracked files pass; a synthetic root-level `member-export.json` is still rejected. See `docs/security/OPERATIONAL_DATA_POLICY.md`.
- The gitleaks CI step scans the full git history. `.gitleaks.toml` allowlists exactly one verified false positive (the recovery password alphabet constant in `services/api/app/modules/identity/service.py`). No real secret is allowlisted.
- Known open security item (HUMAN_REQUIRED): a historical `JWT_SECRET_KEY` value remains in commit `2f03643f` (`docker-compose.prod.yml`). HEAD now fails closed and requires the operator environment, but any deployment that used the committed value must rotate its JWT secret, and the history exposure is tracked for Sprint 101 remediation.

## Sprint Batch Autopilot

```bash
npm run sprint:batch:doctor
npm run sprint:batch:status
npm run sprint:batch:report
```

See `docs/automation/SPRINT_BATCH_AUTOPILOT.md` for the Roadmap V2 execution policy.
