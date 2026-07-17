# Kairo Offer Pack

This document is the short market-facing packaging summary for Kairo.

## Product Summary

Kairo is a local-first association management and private AI workspace for organizations that need:

- clear member and office-role workspaces
- secure document search and chat with citations
- contribution and finance follow-up workflows
- policies, announcements, events, and disciplinary governance
- strict backend-enforced tenant isolation

The current product is a strong release candidate for disciplined self-hosting, association pilots, and service-led deployments.

## Best-Fit Organizations

Kairo is best suited today for:

- associations and clubs with roughly 50 to 200 active members
- organizations that need differentiated office roles
- teams that want private AI over internal documents without giving up backend access control
- self-hosted environments or managed deployments with a named operator

## Offer Shapes

### 1. Self-hosted deployment

Best for organizations that want infrastructure ownership.

Included:

- application delivery package
- deployment runbook
- onboarding guidance
- upgrade and rollback procedure
- support on documented product behavior

Customer responsibility:

- infrastructure hosting
- backups and storage lifecycle
- uptime monitoring
- secret management
- domain, TLS, and network posture

### 2. Managed service

Best for organizations that want an operational service rather than a software-only handoff.

Included:

- hosted runtime
- backup and upgrade operations
- recovery procedure ownership
- first-line operational monitoring
- support workflow and escalation path

Customer responsibility:

- user administration inside the tenant
- business data quality
- policy and role decisions
- document publication governance

### 3. Pilot package

Best for evaluation, donor demonstrations, or first real-world adoption with limited risk.

Included:

- one guided onboarding cycle
- demo-to-production checklist
- role and workflow validation
- limited-duration support window
- success criteria review at the end of the pilot

## Included Product Capabilities

- multi-tenant authentication and tenant switching
- role-aware workspaces for `member`, `secretary_general`, `treasurer`, `auditor`, `censor`, `sports_manager`, `president`, `vice_president`, and `principal_admin`
- member self-service profile, balance, and PDF statement access
- office-role document, governance, finance, and disciplinary workflows within backend-approved boundaries
- multilingual interface baseline with French first, then English and German
- private AI assistant with citations and role-aware refusal behavior
- production-oriented deployment, backup, restore, and rollback runbooks

## Explicit Boundaries

Kairo should be sold today with these explicit limits:

- no promise of enterprise SSO
- no promise of provider-side webhook reconciliation or carrier-grade delivery guarantees on the live notification channels
- no claim that the LLM can override backend permissions
- no claim of generic “AI knows everything”; answers remain source-bound and permission-bound
- no claim of turnkey legal compliance or data-processing sign-off without customer-specific review

## First Contact Material

For a new buyer or association board, start with:

1. `README.md`
2. `docs/commercial/offer-pack.md`
3. `docs/commercial/feature-matrix.md`
4. `docs/commercial/support-playbook.md`
5. `docs/commercial/demo-to-production-checklist.md`

## Commercial Positioning Rule

If the verified runtime surface changes, update this offer pack together with the feature matrix, support playbook, and README.
