# Next Sprint

## Status

Sprint 73 (open-source maturity track) is complete. Sprint 74 through Sprint 86
have been executed and documented as the first increments of the new planning cycle.

## What Was Done

Sprint 88 - Chat Authorization Surface And Domain Guard Expansion:

- Centralized role-aware chat domain decisions in a backend-owned policy
  contract so publication, sports, governance, disciplinary, personal-finance,
  and tenant-finance assistant surfaces stay aligned with real capabilities and
  tenant module toggles
- Added `GET /api/v1/chat/domain-policy` so the frontend suggestion surface no
  longer guesses assistant scope from roles alone
- Updated chat structured-context preparation so protected structured data is
  refused before prompt assembly whenever the role or tenant module contract
  does not authorize that domain
- Aligned the chat view suggested prompts with the backend domain-policy
  response instead of static role heuristics
- Added backend regressions for hidden publication domains, publication refusal,
  sports refusal, and tenant-finance stream refusal when the corresponding
  tenant modules are disabled
- Tightened French publication-intent matching so “contexte officiel de
  publication” now reaches the domain-specific refusal path
- Verified: `python -m pytest services/api/tests/test_chat.py -q`
  (20 passed), `npm run type-check`, and `npm run build` passed on
  July 17, 2026

## Next Planning Cycle

Sprint 74 through Sprint 88 now cover the broader recovery-UX rollout, the
observability packaging baseline, the three currently live operator
notification channels, the acceptance-level reconciliation/audit baseline, the
secure provider callback seam, the replay-safe plus pollable reconciliation
baseline, the operator triage/retry workflow on top of it, the frontend
role-entry parity pass, and the backend-owned chat authorization-surface
alignment. The next agent session should execute
`Sprint 89 - Quality Gate Expansion And CI Hardening`, expanding validation
coverage carefully across linting, typing, backend safety, and browser flows
without destabilizing the current mature role and chat surfaces.

## Continuity Rule

Future agent sessions must not invent the next step from memory. They must read
`README.md`, `AGENTS.md`, `constitution/KAIRO_CONSTITUTION.md`,
`IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`, `prompts/CODEX_AUTOPILOT.md`,
and `prompts/KAIRO_CONTINUE_UNIVERSAL.md`, then decide the next increment.
