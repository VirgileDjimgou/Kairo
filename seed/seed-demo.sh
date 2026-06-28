#!/usr/bin/env bash
# Seed demo data into a running Kairo instance
# Usage: ./seed/seed-demo.sh
docker compose exec api python -m app.db.seed
