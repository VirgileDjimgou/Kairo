# Sprint 1 Codex Prompt

Implement Identity, Tenancy and Auth.

Read first:
- 00_MASTER_PROMPT_CODEX.md
- 01_PROJECT_CONSTITUTION.md
- 02_ARCHITECTURE.md
- 08_DATA_MODEL.md
- 09_SECURITY_AND_LLM_SAFETY.md

Target modules:
- identity
- tenancy

Implement:
- Tenant model
- User model
- TenantUser model
- Role model
- Permission model
- password hashing
- JWT login
- active tenant dependency
- protected test endpoint
- unit/integration tests

Rules:
- every tenant-scoped query requires tenant_id
- do not implement documents yet
- do not implement frontend beyond simple login integration if already available

Acceptance criteria:
- admin can login
- protected endpoint works
- tenant isolation tests pass
