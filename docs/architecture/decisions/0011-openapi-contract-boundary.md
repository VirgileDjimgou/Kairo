# ADR-011: OpenAPI As The Committed Client Contract Boundary

Status: Accepted

## Context

The Vue PWA and the Flutter client consume the FastAPI API through hand-written
gateway types. Before this decision there was no versioned schema in the
repository, no automated breaking-change detection, and no machine check that a
client call still mapped to a documented operation. Drift therefore surfaced only
at runtime.

## Decision

- The FastAPI schema is exported deterministically by
  `services/api/scripts/export_openapi.py` and committed as
  `docs/api/openapi.json`. It is the versioned contract of record.
- `scripts/check-openapi-contract.mjs` regenerates the schema and fails on
  breaking changes: removed paths/operations/parameters/media types, newly
  required request inputs, removed required response properties, type changes and
  enum-value removals. Additive changes are reported and allowed. Intentional
  changes refresh the baseline through `--update`.
- `scripts/generate-client-contracts.mjs` emits typed contracts for both clients:
  `apps/web/src/api/generated/contracts.ts` (interfaces/types plus an
  `ApiOperations` map) and
  `apps/flutter_kairo/lib/core/api/generated/contracts.dart` (typed classes with
  `fromJson`/`toJson` plus `apiOperationIds`). `--check` fails when the committed
  files are stale. The Dart file opts out of formatting and naming lints by
  pragma.
- Generated types coexist with thin hand-written gateways. Gateways keep
  authentication, error handling and response-shape decisions; the generated
  types own field names and shapes. Sprint 114 notification contracts are
  consumed from generated types in the Vue notification gateway and exercised by
  `apps/flutter_kairo/test/contract_parity_test.dart`.
- `scripts/check-client-route-coverage.mjs` verifies that every statically
  visible client call maps to a documented operation. Dynamic path dispatchers
  (for example finance receipt sub-paths) are reported explicitly rather than
  silently ignored.
- `docs/api/CLIENT_FEATURE_PARITY.md` is the feature parity matrix between API
  domains, Vue consumers and Flutter consumers.
- CI runs all three checks in the `contracts` job. Generated types are machine
  output, never an authorization decision.

## Consequences

- Breaking API changes cannot merge unnoticed; the failure message names the
  exact operation or schema.
- Client drift is reduced to the reported dynamic dispatchers, which stay
  bounded by the generated operation list.
- Adding an endpoint requires regenerating the contracts; forgetting to do so
  fails the generated-contract check.
- The schema file is large but reviewable when a contract change is intentional.
