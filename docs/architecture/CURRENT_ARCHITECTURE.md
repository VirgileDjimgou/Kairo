# Kairo — Current Architecture Snapshot

Last verified: 2026-09-26 (Roadmap V2 Sprint 110)

This file is the concise description of what Kairo IS today. When code and this
file disagree, trust the code and update this file. Historical narrative lives in
`IMPLEMENTATION_ROADMAP.md` and `PROJECT_STATUS.md`; active execution lives in
`docs/roadmap/KAIRO_V2_ROADMAP.json`.

## Shape

Kairo is a **modular monolith** (see ADR-001): one FastAPI application, one
PostgreSQL database, one Celery worker, shared Redis/MinIO/Qdrant. There are no
microservices and no message broker beyond the existing Redis-backed Celery
queue and the PostgreSQL notification outbox.

```
Vue 3 PWA (apps/web)          Flutter client (apps/flutter_kairo)
   |   consumes API contracts only        |  Android + Flutter Web first
   +-------------------+------------------+
                       v
        FastAPI modular monolith (services/api/app)
        core/ identity/ tenancy/ membership/ contributions/
        governance/ disciplinary/ events/ announcements/ documents/
        notifications/ audit/ chat/ rag/ backup/ worker/
                       |
     +---------+-------+--------+-----------+
     v         v       v        v           v
 PostgreSQL   Redis   MinIO   Qdrant   Ollama/Qdrant (optional private AI)
             Celery   objects  vectors
```

## Load-bearing boundaries

- **Backend is the only policy enforcement point** (ADR-002). Roles,
  capabilities, tenant isolation and module entitlements are enforced in FastAPI
  dependencies and services. The frontend only shapes presentation.
- **Every tenant-scoped query includes `tenant_id`.** Cross-tenant reads are
  treated as security defects.
- **RAG authorization happens before prompt assembly** (ADR-003). Retrieved
  chunks are filtered by tenant and access scope before anything reaches the
  LLM; unauthorized chunks are never sent to the model and the LLM never decides
  access.
- **Notifications are delivery hints** (ADR-004). The authenticated,
  tenant-scoped inbox is the source of truth; Web Push (VAPID) and Android FCM
  carry generic bodies only. A PostgreSQL-backed transactional outbox keeps
  notification side effects out of business transactions.
- **Operational documents never enter Git** (ADR-007). Association documents
  live in MinIO/S3 through the document module.

## Identity and tenancy

- JWT access tokens bound to a tenant; refresh validated against persistent
  sessions; MFA (TOTP); invitations; assisted one-time recovery passwords;
  session inventory and revocation. (`services/api/app/modules/identity/`)
- Tenant membership resolution, branding and module toggles per tenant.
  (`services/api/app/modules/tenancy/`)
- Canonical office roles: member, secretary_general, treasurer, auditor, censor,
  sports_manager, president, vice_president, principal_admin (+ legacy `admin`).
- Roles are capability bundles. Effective capabilities are exposed read-only on
  `GET /auth/me` (active tenant) and on each tenant membership, and the clients
  use them for navigation and action visibility. Backend enforcement still
  checks the specific capability per endpoint; presentation-scoped capabilities
  never gate an authorization decision (ADR-008).

## Business modules

| Domain | Backend module | Notes |
| --- | --- | --- |
| Members | `membership/` | profiles, lifecycle, statement |
| Finance | `contributions/` (models, schemas, repository, router) + `finance/` (bounded context) | contributions, payments, receipts + custody handover, expenses, budgets, exports, reminders. `finance/` holds the decomposed domains (`contributions`, `receipts`, `custody`, `expenses`, `budgeting`, `reminders`, `reporting`), a notification contract seam (`notifications.py`) and a `ContributionService` facade; `contributions/service.py` re-exports the facade for API compatibility. Each command keeps its own transaction. |
| Governance | `disciplinary/`, `events/`, `announcements/`, policies | role-scoped visibility |
| Knowledge | `documents/`, `rag/`, `chat/` | ingestion, citations, refusal behavior |
| Operations | `audit/`, `backup/`, `notifications/`, `worker/` | journal, encrypted backups, outbox delivery |

## Clients

- **Vue 3 PWA** (`apps/web`) — production client. Pinia stores, vue-router,
  typed API gateways under `src/api/`, shared capability constants under
  `src/config/capabilities.ts`, and domain feature modules under `src/features/`
  (`finance`, `dashboard`, `members`, `attention`, `search`). Router views are
  thin containers that orchestrate feature components and composables;
  navigation and action visibility follow API capabilities, and no
  authorization decision is made in the client.
- **Flutter client** (`apps/flutter_kairo/`) — parallel Android + Flutter Web
  client, same API contracts, no local authorization decisions. The PWA is never
  replaced by it (see `docs/flutter/`).

## Runtime and deployment

- Docker Compose stack (api, worker, web, postgres, redis, minio, qdrant,
  ollama, cloudflared); production override `docker-compose.prod.yml` fails
  closed on missing secrets.
- Cloudflare Tunnel ingress; Nginx serves the built PWA and proxies `/api/`.
- Encrypted, signed PostgreSQL/MinIO backup archives with restore drills.

## Quality gates

Backend `ruff` + `mypy` + `pytest` (303 tests), Web `vue-tsc` + `vite build` +
three Playwright packs (locale, roles, release-candidate), Flutter `analyze` +
`test` + web/Android builds, repository guards (`check-sensitive-files`,
`check-i18n-coverage`, `check-api-collection-paths`) and gitleaks history scan.
Commands of record: `docs/operations/validation-baseline.md`.

## Known structural debt (tracked in Roadmap V2)

- Oversized services: `identity/service.py`, `chat/service.py`; monolithic
  `messages.ts`; remaining large admin views (`AdminDocumentsView.vue`,
  `AdminNotificationsView.vue`).
- Sprint 110 decomposed the 1174-line `contributions/service.py` into the
  `app/modules/finance/` bounded context (largest domain file 349 lines, public
  facade 29 lines) without changing API contracts or finance semantics; report
  generation and notification triggering are separated behind domain modules
  and a notification contract seam.
- Sprint 107 decomposed the finance, dashboard and member-admin mega-views into
  `src/features/` modules (finance workspace 1252 → 216 lines, dashboard
  823 → 104, member admin 771 → 170) without changing behavior or moving
  authorization into the frontend.
- Status: remaining items are addressed by Roadmap V2 sprints 108–113
  (i18n, capabilities, domain events, service decomposition).
