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

## Reporting Issues

Open an issue using the most relevant template below.

- **Bug report**: include the exact command or URL, the expected behavior, the actual behavior, and the backend/frontend logs (redacted of any tenant data, emails, or tokens).
- **Feature request**: describe the association workflow, the role that needs it, and why the current surface does not cover it.
- **Documentation**: point to the file and the section that is unclear or outdated.

Do not include secrets, passwords, JWTs, upload contents, or member data in issues. Kairo is multi-tenant: never paste real tenant data.

## Pull Requests

- Keep PRs small and scoped to one concern.
- Add or update backend tests for any behavior change. Frontend changes should keep `npm run type-check` and `npm run build` green.
- The backend remains the only enforcement point for tenant isolation and permissions. Do not move access decisions into the frontend or the LLM.
- Update `IMPLEMENTATION_ROADMAP.md` and `PROJECT_STATUS.md` only when a sprint is completed, and keep `docs/ai/NEXT_SPRINT.md` pointing at the next planned sprint.
- Reference the related issue or roadmap sprint in the PR description.

## Security Disclosures

Do not open public issues for security vulnerabilities. Report them privately to the maintainers through the security advisory channel of the repository. Include:

- a clear description of the affected flow (module, endpoint, or role),
- steps to reproduce,
- the expected vs actual authorization outcome,
- redacted evidence (no real tenant data, tokens, or member records).

Security-sensitive areas include tenant isolation, cross-member data exposure, RAG retrieval filtering before prompt assembly, and admin/sensitive route protection.

## Known Limits And Next Steps

Kairo is a mature open-source release candidate, not a finished commercial platform. See [docs/OPEN_SOURCE_RELEASE.md](docs/OPEN_SOURCE_RELEASE.md) for the honest known limits and the next planning cycle.

## License

MIT — see [LICENSE](LICENSE).
