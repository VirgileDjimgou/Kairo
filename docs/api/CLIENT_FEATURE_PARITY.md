# Client Feature Parity — API Contract Boundary

Last verified: 2026-09-26 (Roadmap V2 Sprint 115)

FastAPI's OpenAPI schema is the formal boundary between the backend and both
clients. `docs/api/openapi.json` is the committed, versioned schema;
`node scripts/check-openapi-contract.mjs` fails on breaking changes;
`node scripts/generate-client-contracts.mjs --check` fails on stale generated
types; `node scripts/check-client-route-coverage.mjs` fails when a literal client
call no longer maps to a documented operation.

## Generated contracts

| Client | Generated file | Contents |
| --- | --- | --- |
| Vue PWA | `apps/web/src/api/generated/contracts.ts` | Interfaces/types for every component schema, plus `ApiOperations` (method + path → request/response types). Notification inbox/push/health contracts are imported by `notifications.api.ts`. |
| Flutter | `apps/flutter_kairo/lib/core/api/generated/contracts.dart` | Typed classes with `fromJson`/`toJson` for every component schema, plus `apiOperationIds`. Notification contracts are exercised by `test/contract_parity_test.dart`. |

## Feature parity matrix

| Domain | Representative operations | Vue consumer | Flutter consumer | Evidence |
| --- | --- | --- | --- | --- |
| Authentication, MFA, sessions | `POST /api/v1/auth/login`, `POST /api/v1/auth/mfa/complete`, `GET /api/v1/auth/sessions` | `src/api/auth.api.ts` | `features/auth/data/auth_gateway.dart` | Route coverage + F1 tests |
| Tenancy and profile | `GET /api/v1/auth/me`, `POST /api/v1/auth/switch-tenant` | `src/api/auth.api.ts`, `stores/tenant.store.ts` | `auth_gateway.dart` | Route coverage + role packs |
| Members | `GET /api/v1/memberships/`, `POST /api/v1/memberships/`, `PATCH /api/v1/memberships/{id}` | `src/api/members.api.ts` | `features/members/data/member_gateway.dart` | Route coverage + F2 tests |
| Contributions and finance | `GET /api/v1/contributions/summary`, `POST /api/v1/contributions/payments`, `GET /api/v1/contributions/report/export/{export_format}` | `src/features/finance/**` | `features/finance/data/finance_gateway.dart` | Route coverage + F3/F4 tests; dynamic path dispatchers reported by the guard |
| Receipts and custody | `POST /api/v1/contributions/receipt-declarations`, `POST .../{id}/process`, `POST .../{id}/confirm-treasury-receipt` | `src/features/finance/**` | `features/finance/data/receipt_gateway.dart` | Route coverage + F3 tests; dynamic paths reported |
| Expenses and budget | `POST /api/v1/contributions/expenses`, `GET /api/v1/contributions/annual-budget` | `src/features/finance/**` | `finance_gateway.dart` | Route coverage + F4 tests |
| Notifications (Sprint 114) | `GET /api/v1/notifications/inbox`, `PUT /api/v1/notifications/preferences`, `POST /api/v1/notifications/devices/{installation_id}/revoke`, `GET /api/v1/notifications/health` | `src/api/notifications.api.ts` (generated types) | `features/notifications/data/inbox_gateway.dart` | Generated types on both clients + `contract_parity_test.dart` + convergence tests |
| Chat and assistant | `POST /api/v1/chat/query-stream`, `GET /api/v1/chat/conversations` | `src/api/chat.api.ts` | `features/chat/data/chat_gateway.dart` | Route coverage + F6 tests; SSE stream is not an OpenAPI JSON operation |
| Governance: policies, events, announcements, discipline, documents | `GET /api/v1/policies/`, `POST /api/v1/events/`, `POST /api/v1/announcements/`, `POST /api/v1/disciplinary/`, `POST /api/v1/documents/upload` | `src/api/*.api.ts` | `features/governance/data/governance_gateway.dart` | Route coverage + F5 tests |
| Search and attention | `GET /api/v1/search`, `GET /api/v1/attention` | `src/api/search.api.ts`, `src/api/attention.api.ts` | `features/foundation/presentation/role_shell.dart` (attention) | Route coverage + S105/S106 tests |
| Operation journal, audit, recovery | `GET /api/v1/admin/audit/operation-journal`, `GET /api/v1/recovery/backups` | `src/api/audit.api.ts` | `features/governance/data/operation_journal_gateway.dart` | Route coverage; operation journal appends query suffixes dynamically |
| System | `GET /health`, `GET /metrics` | `src/api/system.api.ts` | — (operator surface only) | Route coverage |
| Module registry | `GET /api/v1/modules`, `GET /api/v1/modules/{module_key}` | — (clients may adopt incrementally) | — (clients may adopt incrementally) | `test_module_registry.py` + route coverage |

## Intentional differences

- Flutter Web intentionally has no Web Push; browser push is owned by the Vue PWA
  service worker.
- System/operator endpoints (`/metrics`, `/health`, notification operator
  channels) are consumed by the Vue admin console only.
- Dynamic path dispatchers in the Flutter finance/receipt/governance gateways are
  reported by the coverage guard but not statically verifiable; the generated
  operation list is the source of truth for those domains.

## Commands

```bash
node scripts/check-openapi-contract.mjs        # breaking-change detector
node scripts/check-openapi-contract.mjs --update   # intentional baseline refresh
node scripts/generate-client-contracts.mjs     # regenerate TS + Dart contracts
node scripts/generate-client-contracts.mjs --check # drift check
node scripts/check-client-route-coverage.mjs   # client call ↔ operation mapping
npm run contracts:check                        # all three
```
