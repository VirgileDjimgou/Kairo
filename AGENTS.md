# Kairo Agent Guide

This repository is designed to be continued from multiple agentic IDEs, including Codex, Cursor, and GitHub Copilot.

## Purpose

Use this file as the universal entry point before implementing or reviewing anything.

## Read Order

Read these files in this order at the beginning of every new session:

1. `README.md`
2. `AGENTS.md`
3. `constitution/KAIRO_CONSTITUTION.md`
4. `IMPLEMENTATION_ROADMAP.md`
5. `PROJECT_STATUS.md`
6. `prompts/CODEX_AUTOPILOT.md`
7. `orgmind_prompt_pack/01_PROJECT_CONSTITUTION.md`
8. `orgmind_prompt_pack/02_ARCHITECTURE.md`
9. `orgmind_prompt_pack/03_ROADMAP_SPRINTS.md`
10. `orgmind_prompt_pack/09_SECURITY_AND_LLM_SAFETY.md`

If architecture or behavior is unclear, inspect the code before making assumptions.

## Conflict Resolution

If two sources disagree, use this order:

1. Verified code and tests
2. `PROJECT_STATUS.md`
3. `IMPLEMENTATION_ROADMAP.md`
4. `constitution/KAIRO_CONSTITUTION.md`
5. `orgmind_prompt_pack/`
6. `README.md`

If code and docs diverge, trust verified code first, then update the docs you touched.

## Non-Negotiable Rules

- Never hardcode COMBIS as product logic. It is a demo tenant only.
- Every tenant-scoped query must include `tenant_id`.
- The backend is the only policy enforcement point.
- The LLM never decides access control.
- Retrieval filtering must happen before prompt assembly.
- Never send unauthorized chunks to the LLM.
- Frontend code must consume API contracts only.
- Preserve the modular monolith structure unless a documented ADR justifies change.
- Update tests and documentation when behavior changes.
- Use English for code, identifiers, comments, tests, and file names.

## Sprint Continuity Workflow

For every new coding session:

1. Run `git status --short`.
2. Read the files listed in the read order above.
3. Confirm the active sprint from `PROJECT_STATUS.md` and `IMPLEMENTATION_ROADMAP.md`.
4. Implement only that sprint or an explicitly requested stabilization task.
5. Do not silently skip ahead to later roadmap modules.
6. Run the most relevant tests for the touched area.
7. Update `PROJECT_STATUS.md` and `IMPLEMENTATION_ROADMAP.md` if the sprint state changed.

## Expected Engineering Style

- Small vertical slices.
- Explicit naming.
- Thin routers, service orchestration, repository isolation.
- Provider abstractions for external services.
- Typed DTOs at API boundaries.
- No unrelated refactors during sprint work.

## Done Means

A sprint increment is done only when:

- the implementation compiles or builds,
- relevant tests pass,
- tenant isolation is preserved,
- permissions are enforced in the backend,
- docs are updated,
- the feature is demonstrable in the current repo.

## Translation Governance

Kairo uses a French-first, English-second, German-third i18n contract.

- All user-facing strings in Vue templates must use `localeStore.t('key')` or the `t()` helper.
- Never add hardcoded English, French, or German strings directly in templates.
- All new i18n keys must be added to all three locales (`fr`, `en`, `de`) in `apps/web/src/i18n/messages.ts`.
- The `localeStore` is imported from `@/stores/locale.store`.
- Views may use an inline `copy` computed pattern for view-specific strings, but this pattern must switch on `localeStore.currentLocale` and cover all three locales.
- Backend enum values (status, scope, method) are not i18n strings — keep them as-is.
- Run `node scripts/check-i18n-coverage.mjs` to scan for potential hardcoded strings.
- Future UI copy additions must have an obvious home in `messages.ts` and a validation path.

