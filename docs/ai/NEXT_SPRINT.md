# Next Sprint

## Status

Sprint 93 (Frontend Type Contract Hardening) is complete.

## What Was Done

Sprint 93 made the existing strict frontend compiler contract materially stronger.

Key fixes:
- Enabled `exactOptionalPropertyTypes` and `noUncheckedIndexedAccess` in the Vue TypeScript configuration.
- Corrected optional HTTP payloads, filters, streaming request options, stores, and list access to make absent values explicit rather than sending `undefined`.
- Aligned the notification-history Playwright fixture with the current `{ items, summary }` API response and query-string request contract.

Verified: frontend type-check and production build pass; the localization browser suite passes 20/20.

## Next Planning Cycle

Sprint 94 - Role Journey Browser Coverage Expansion should add focused browser journeys for the highest-risk member and office permissions, beginning with tenant switching, member finance self-service, and direct-route denials. The backend remains the source of authorization truth; browser checks only prove that the UI follows it.

## Continuity Rule

Future agent sessions must not invent the next step from memory. They must read
`README.md`, `AGENTS.md`, `constitution/KAIRO_CONSTITUTION.md`,
`IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`, `prompts/CODEX_AUTOPILOT.md`,
and `prompts/KAIRO_CONTINUE_UNIVERSAL.md`, then decide the next increment.
