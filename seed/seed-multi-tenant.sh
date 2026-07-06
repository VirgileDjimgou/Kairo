#!/usr/bin/env bash
# Seed the base demo tenant plus a second tenant for multi-tenant demos.
# Usage: ./seed/seed-multi-tenant.sh
docker compose exec api python -m app.db.seed_multi_tenant
