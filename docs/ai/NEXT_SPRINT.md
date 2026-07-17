# Next Sprint

## Status

Sprint 73 (open-source maturity track) is complete. Sprint 74 through Sprint 85
have been executed and documented as the first increments of the new planning cycle.

## What Was Done

Sprint 85 - Notification Reconciliation Polling And Replay-Safety Baseline:

- Added replay-safe reconciliation handling so duplicate final-state callbacks
  for the same tenant, channel, and provider reference now return
  `updated=false` instead of duplicating backend audit evidence
- Added conflict protection so a mismatched second final-state update for an
  already reconciled dispatch is rejected instead of overwriting trusted
  notification history
- Added `POST /api/v1/notifications/reconciliation/poll` for tenant-admin and
  principal-admin users, keeping status lookup strictly backend-owned and
  tenant-scoped
- Extended the notification provider contract with a delivery-status lookup seam
  and activated controlled polling for the gateway-backed WhatsApp path
- Extended notification channel, dispatch, and history payloads with
  `polling_supported`, then updated the admin notifications workspace so
  operators can refresh still-pending deliveries directly from audited history
  when a provider supports it
- Added backend regression coverage for replay-safe callbacks, successful
  polling to a final delivered state, and clean rejection for channels that do
  not support polling
- Verified: `python -m pytest services/api/tests/test_notifications.py -q`
  (22 passed), `npm run type-check`, and `npm run build` pass

## Next Planning Cycle

Sprint 74 through Sprint 85 now cover the broader recovery-UX rollout, the
observability packaging baseline, the three currently live operator
notification channels, the acceptance-level reconciliation/audit baseline, the
secure provider callback seam, and the replay-safe plus pollable reconciliation
baseline. The next agent session should execute
`Sprint 86 - Notification Reconciliation Operations And Stale-Delivery Triage Baseline`,
improving operator triage and safe retry ergonomics for stale pending or failed
deliveries without widening permissions.

## Continuity Rule

Future agent sessions must not invent the next step from memory. They must read
`README.md`, `AGENTS.md`, `constitution/KAIRO_CONSTITUTION.md`,
`IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`, `prompts/CODEX_AUTOPILOT.md`,
and `prompts/KAIRO_CONTINUE_UNIVERSAL.md`, then decide the next increment.
