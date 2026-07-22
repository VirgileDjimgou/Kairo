# Next Sprint

## Status

Sprint 98 (Operational Pilot Acceptance) is in progress.

## What Was Done

Sprint 98 established the non-disclosing readiness gate for a real operational pilot.

What was added:
- Added `scripts/pilot_acceptance_preflight.ps1`, which reports only pass/fail production-readiness requirements and never prints secret values.
- Added `scripts/start_quick_demo.ps1` and `scripts/stop_quick_demo.ps1` for a no-domain, no-token demonstration flow. They keep `.env` unchanged, use a temporary ignored environment file, and expose only the web and API endpoints through ephemeral Quick Tunnels.
- Documented the pilot preflight in deployment, validation, and go-live material.
- Verified that the current local development environment fails closed when it lacks production secrets, HTTPS, and a tunnel token.

Current blockers: a customer-ready secret set, a real domain or Cloudflare Tunnel token, and an approved backup/restore-drill target are not available in this repository.

## Next Planning Cycle

Resume Sprint 98 when those operational inputs are available. It must validate the environment, run the gateway smoke check through HTTPS, record a backup archive, restore it only into an approved isolated target, and retain backend-owned authorization throughout.

## Continuity Rule

Future agent sessions must not invent the next step from memory. They must read
`README.md`, `AGENTS.md`, `constitution/KAIRO_CONSTITUTION.md`,
`IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`, `prompts/CODEX_AUTOPILOT.md`,
and `prompts/KAIRO_CONTINUE_UNIVERSAL.md`, then decide the next increment.
