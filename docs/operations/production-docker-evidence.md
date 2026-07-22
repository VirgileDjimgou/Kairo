# Production Docker Evidence

Last verified: 2026-07-22

## Scope

This record captures a local production Compose validation. It verifies the
production image path and public gateway behavior only; it does not replace a
customer-specific deployment, backup drill, or functional acceptance test.

## Verified Local Stack

- Docker Desktop server: `28.0.1`
- Compose files: `docker-compose.yml` plus `docker-compose.prod.yml`
- Isolated Compose project: `kairo-s97`
- Startup command: `docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p kairo-s97 up -d --build`
- Web production image: built successfully with `VITE_API_BASE_URL=/api/v1`

## Gateway Results

The production Nginx gateway returned the expected results at
`http://localhost`:

- `/`: `200`
- `/health`: `200`
- `/metrics`: `200`
- `/docs`: `404`
- `/redoc`: `404`
- `/openapi.json`: `404`

The bundle was also checked to ensure it contains `/api/v1` and does not
contain the development-only `http://localhost:8000/api/v1` endpoint.

## Reproduction

Use a production-ready environment file with non-placeholder secrets. On
Windows, run the production Compose command and then:

```powershell
.\scripts\production_smoke.ps1 -BaseUrl http://localhost
```

The existing install, upgrade, backup, and rollback helpers remain Bash
scripts and require a Bash-compatible environment.
