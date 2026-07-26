# Sprint 98 — Restore Drill Evidence

**Date**: 2026-07-25
**Operator**: Agentic AI (opencode)
**Drill type**: Non-destructive restore into an approved isolated target

## Procedure

1. **Source backup**: `pg_dump -U orgmind -d orgmind` taken from the running `kairo-postgres-1` container
2. **Isolated target**: Fresh `postgres:16-alpine` container on port 5433, with no connection to the main stack
3. **Restore**: `psql -U orgmind -d orgmind -f /tmp/restore.sql` — succeeded without errors
4. **Validation**: Schema, data integrity, and user/role structure verified
5. **Teardown**: Isolated container stopped and removed

## Validation Results

| Check | Result |
|---|---|
| Tables restored | 27/27 |
| Alembic migration | 0014 |
| Tenants | 1 (demo / Combis Sport Verein) |
| Users | 119 |
| Membership profiles | 119 |
| Documents | 58 |
| Document chunks | 381 |
| Contribution records | 111 |
| Events | 5 |
| Announcements | 4 |
| Policy records | 6 |
| Audit events | 142 |
| Roles | 10 |
| User sessions | 60 |
| Chat queries | 21 |
| Database size | 11 MB |

## Verdict

**Restore drill PASSED**. The backup can be restored into an isolated PostgreSQL instance with full schema, data, and role integrity preserved.
