# Customer Onboarding Guide

This guide is written for a new evaluator or customer team starting from a delivered Kairo environment.

## Prerequisites

- A working Docker Compose deployment or equivalent infrastructure
- A configured `.env` file with production secrets
- At least one tenant admin account
- A decision on whether the deployment is self-hosted or managed-service

## First Login Path

1. Open the public application URL.
2. Sign in with the tenant administrator account.
3. Confirm the active tenant and branding are correct.
4. Open the onboarding wizard at `/admin/onboarding` and review the first-run checklist.
5. Use the next best action or the guided links to continue setup.
6. Open `/health` and confirm the platform is reachable.

## Initial Tenant Setup

After first login, the tenant admin should:

1. Review tenant name, branding, and module toggles.
2. Use the onboarding wizard to move through settings, documents, members, announcements, and events in a predictable order.
3. Create or import the first member profiles.
4. Publish the first announcement or event if those modules are enabled.
5. Confirm roles are assigned correctly.
6. Upload one test document and verify ingestion.
7. Run one RAG query and confirm citations appear.
8. If you need a second tenant for browser demos, run the multi-tenant seed helper:
   - macOS / Linux: `./seed/seed-multi-tenant.sh`
   - Windows PowerShell: `.\seed\seed-multi-tenant.ps1`

## Data Preparation

Recommended launch data:

- tenant organization name
- admin users
- member list
- contribution records or financial opening balance
- policy documents
- key operational documents
- events and announcements

## Success Criteria

Onboarding is complete when:

- the tenant admin can log in and switch tenants if needed
- core modules are visible only when enabled
- the dashboard gives an explicit first-run checklist instead of a dead-end empty page
- empty states for documents and members point to real next actions
- the customer understands where documents, members, and support requests live
- backups are scheduled or handed off
- the customer knows the support boundary and escalation path

## Notes

- The frontend should never be the only source of truth for tenant access.
- The backend remains the authority for permissions, data isolation, and module enforcement.
