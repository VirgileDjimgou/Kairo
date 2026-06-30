# Contributing to Kairo

## Quick Start

See [README.md](README.md#quick-start) for setup instructions.

## Development

```bash
# Backend tests (SQLite by default — no local PostgreSQL needed)
cd services/api
pip install -r requirements.txt
pytest

# Frontend dev server
cd apps/web
npm install
npm run dev

# Frontend production build (type-check + bundle)
npm run build
```

## Project Structure

| Path | Purpose |
|------|---------|
| `services/api/app/modules/` | Domain modules (one per feature) |
| `services/api/app/core/` | Shared infrastructure (auth, config, providers) |
| `services/api/app/db/` | Database session, migrations, seed |
| `services/api/tests/` | Backend integration tests |
| `apps/web/src/views/` | Frontend views (admin, member, auth) |
| `apps/web/src/api/` | API client modules |
| `apps/web/src/stores/` | Pinia stores (auth, tenant) |
| `infra/` | Production config (nginx, caddy, cloudflare) |
| `scripts/` | Backup, restore, smoke test scripts |
| `seed/` | Demo data helpers and sample CSV files |
| `docs/` | Architecture, deployment, commercial docs |

## Coding Conventions

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy async, Pydantic v2
- **Frontend**: Vue 3 Composition API, TypeScript, Pinia, Bootstrap 5
- **Tests**: pytest with pytest-asyncio, httpx AsyncClient, SQLite
- **Tenant isolation**: every DB query includes `tenant_id`
- **Permissions**: enforced by the backend only — the LLM never decides access
- **Modular monolith**: each feature lives in `app/modules/<name>/` with its own router, schemas, service, and models

## Running Tests

```bash
# All backend tests
cd services/api && pytest

# Specific test file
pytest tests/test_membership.py -v

# With filter
pytest -k "tenant_isolation" -v
```

Tests use SQLite by default and require no external infrastructure.

## Submitting Changes

1. Make focused, single-purpose commits
2. Update tests for any changed behavior
3. Update docs if the change affects setup, configuration, or API contracts
4. Ensure all tests pass before submitting
5. Follow the existing code style (no unrelated refactoring)

## License

MIT — see [LICENSE](LICENSE).
