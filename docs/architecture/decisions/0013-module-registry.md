# ADR-013: Internal Module Registry For Composition And Extension

Status: Accepted

## Context

Before this decision, adding a module required edits in several unrelated central
files: `app/main.py` router imports and `include_router` calls, the module-toggle
key list, the global-search provider list, the chat context provider list, and
health checks. Module metadata (navigation, capabilities, dependencies, domain
events) existed only implicitly across those files, so composition and
extensibility were expensive and drift-prone.

## Decision

- Every module package may ship a `module.py` with a `MODULE` descriptor
  (`app/modules/module_registry/descriptor.py`). A descriptor declares: module
  key, name/description, canonical capabilities, dependencies, default/toggle
  flags, feature flag, router references, search provider references, optional AI
  context provider references, domain event types, navigation metadata and an
  optional health-check hook.
- The registry discovers descriptors by scanning the repository's own
  `app.modules` package tree (`discover_descriptors`). This is an internal product
  extension framework only: there is no arbitrary untrusted plugin execution, no
  dynamic code loading from user input, and no runtime marketplace.
- Validation is fail-fast at first use: duplicate module keys, unknown or
  self/cyclic dependencies, duplicate navigation keys, malformed descriptor
  fields and unknown capability strings raise `ModuleRegistryError`.
- Central composition consumes the registry:
  - `app/main.py` includes routers from `default_registry().routers()` in
    descriptor order (preserving the previous route order, verified by the
    OpenAPI contract check);
  - `module_toggles.ALL_MODULES` is derived from descriptors with
    `tenant_toggle=True` (same eight keys as before);
  - `search.providers.default_providers()` is composed from descriptor search
    hooks (same providers and order as before);
  - `chat.contexts.registry.build_default_registry()` appends optional
    descriptor-provided AI context providers after the six core providers;
  - `health_checks.run_all_checks()` merges registered module health hooks after
    the core checks (and never lets a broken hook hide core health).
- Navigation metadata is exposed read-only through
  `GET /api/v1/modules` and `GET /api/v1/modules/{key}`, filtered by the active
  tenant's module toggles and the authenticated user's capabilities. Clients may
  consume it incrementally; the backend remains the only policy enforcement
  point.
- Tenant-specific role bundles are prepared without touching canonical roles:
  `roles.capabilities_json` stores a validated subset of the canonical
  capability catalog (migration 0033), created through
  `POST /api/v1/tenants/{tenant_id}/roles`; canonical role codes cannot be
  replaced, and effective capabilities (JWT `capabilities` claim, `/auth/me`,
  memberships) merge canonical definitions with bundle capabilities.
- A minimal non-critical sample module (`app/modules/sample/`) demonstrates
  automatic discovery: it declares a dependency, a capability-gated read-only
  route and is listed by the registry without any central-file edit.

## Consequences

- Adding a module means adding one package with a descriptor; central files do
  not change. Registry tests prove discovery, validation, router composition,
  search/AI/health hooks and navigation responses.
- The OpenAPI path/method set is protected by the existing contract check, so
  composition changes cannot silently drop or rename routes.
- Navigation metadata is available server-side for both clients, but the Vue and
  Flutter sidebars keep their current curated navigation until they adopt the
  endpoint deliberately.
- Capability enforcement still uses canonical role bundles plus validated tenant
  bundles; the LLM and clients never decide access.
