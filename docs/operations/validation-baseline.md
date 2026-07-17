# Validation Baseline

Last updated: 2026-07-15

This document captures the active quality-gate commands that are expected to work from the repository root unless noted otherwise.

## Backend

Run the full backend suite from the repository root:

```bash
python -m pytest services/api/tests -q
```

Run the active Ruff baseline:

```bash
python -m ruff check \
  services/api/app/core/dependencies.py \
  services/api/app/core/security.py \
  services/api/app/core/authorization.py \
  services/api/app/modules/rag/policy.py \
  services/api/tests/conftest.py \
  services/api/tests/test_chat.py \
  services/api/tests/test_governance_roles.py
```

Run the active Mypy baseline:

```bash
python -m mypy --config-file services/api/pyproject.toml --explicit-package-bases \
  services/api/app/core/dependencies.py \
  services/api/app/core/security.py \
  services/api/app/core/authorization.py \
  services/api/app/modules/rag/policy.py
```

Notes:

- The backend test suite defaults to an isolated SQLite database when `TEST_DATABASE_URL` is not set to PostgreSQL.
- The typed subset is intentionally scoped to the shared authorization and RAG policy path that future role and privacy work depends on.

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
