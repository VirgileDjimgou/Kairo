# Seed the base demo tenant plus a second tenant for multi-tenant demos.
# Usage: .\seed\seed-multi-tenant.ps1
docker compose exec api python -m app.db.seed_multi_tenant
