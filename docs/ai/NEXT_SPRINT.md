# Next Sprint

## Status

Sprint 98 (Operational Pilot Acceptance) is in progress.

## What Was Done

Sprint 98 established the non-disclosing readiness gate for a real operational pilot.

What was added:
- Added `scripts/pilot_acceptance_preflight.ps1`, which reports only pass/fail production-readiness requirements and never prints secret values.
- Added `scripts/start_quick_demo.ps1` and `scripts/stop_quick_demo.ps1` for a no-domain, no-token demonstration flow. They keep `.env` unchanged, use a temporary ignored environment file, and expose only the web and API endpoints through ephemeral Quick Tunnels.
- Added a controlled workbook-import utility that preserves office accounts and operational tenant content while replacing member-only profiles and their finance data from a validated local workbook.
- Documented the pilot preflight in deployment, validation, and go-live material.
- Deployed the named `kairo-production` Cloudflare Tunnel for `https://app.combissportverein.org` with same-origin routing to the private Docker `web` service.
- Generated local production secrets, created a private PostgreSQL backup before credential rotation, and passed the external HTTPS smoke check (6/6).
- Removed the production environment file from the `cloudflared` container to prevent unrelated secrets and the tunnel token from appearing in connector environment logs.
- Corrected production-only Docker health checks and removed the web host-port mapping so Cloudflare Tunnel is the only intended public ingress.

Current blocker: an approved isolated restore target and a recorded non-destructive restore drill are still required.

## Next Planning Cycle

Resume Sprint 98 with the isolated restore drill only. It must restore a backup into an approved isolated target, validate it without exposing data publicly, record the evidence, and retain backend-owned authorization throughout.

## Continuity Rule

Future agent sessions must not invent the next step from memory. They must read
`README.md`, `AGENTS.md`, `constitution/KAIRO_CONSTITUTION.md`,
`IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`, `prompts/CODEX_AUTOPILOT.md`,
and `prompts/KAIRO_CONTINUE_UNIVERSAL.md`, then decide the next increment.
