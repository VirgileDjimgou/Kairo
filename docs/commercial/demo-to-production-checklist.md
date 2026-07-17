# Demo To Production Checklist

Use this checklist when moving from the demo tenant to a real customer deployment.

## Before Cutover

- [ ] Confirm the customer has accepted the feature matrix
- [ ] Confirm the support boundary is understood
- [ ] Confirm the domain and TLS setup
- [ ] Confirm backup storage is available
- [ ] Confirm the production `.env` file has unique secrets
- [ ] Confirm module toggles match the customer scope
- [ ] Review the onboarding wizard and decide whether the demo seed helper should be used for staging only

## Data Preparation

- [ ] Export or recreate the tenant-specific users
- [ ] Prepare member data and contribution opening balances
- [ ] Prepare policies, documents, events, and announcements
- [ ] Remove demo-only content
- [ ] Review tenant branding and contact information
- [ ] If a reproducible second tenant is needed for demos, run `./seed/seed-multi-tenant.sh` or `.\seed\seed-multi-tenant.ps1`

## Infrastructure Cutover

- [ ] Run `bash scripts/deploy_release.sh preflight`
- [ ] Build or deploy through the documented release helper path
- [ ] Apply the target upgrade path with a recorded backup
- [ ] Run `/health`
- [ ] Run `/metrics`
- [ ] Run the production smoke script

## Validation

- [ ] Login works for at least one admin and one member
- [ ] Document upload and retrieval work
- [ ] Invitations and password reset work
- [ ] Audit trail records sensitive actions
- [ ] Disabled modules stay hidden and return backend 403s if accessed directly

## Go-Live Handoff

- [ ] Backup job is scheduled
- [ ] Restore procedure is documented
- [ ] Support contacts are recorded
- [ ] Upgrade procedure is recorded
- [ ] First-week success criteria are defined
