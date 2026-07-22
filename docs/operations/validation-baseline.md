# Validation Baseline

Last updated: 2026-07-21

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

Notes:

- `apps/web/playwright.config.ts` now selects `npm.cmd` on Windows and `npm` elsewhere so the same Playwright suite can run locally and in Linux CI.
- The localization pack is the current browser baseline because it exercises the FR-first contract, authenticated session bootstrapping, principal-admin admin surfaces, and the role-scoped workspaces most affected by recent changes.
- `vue-tsc` runs with `strict`, `exactOptionalPropertyTypes`, and `noUncheckedIndexedAccess`, so optional API fields and list access must be handled explicitly.
