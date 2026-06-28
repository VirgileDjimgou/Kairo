# Seed demo data into a running Kairo instance
# Usage: .\seed\seed-demo.ps1
docker compose exec api python -m app.db.seed
