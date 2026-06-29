# Administrator Guide

This guide is for tenant administrators who operate Kairo after go-live.

## Daily Tasks

- Check the admin overview for readiness signals, warnings, and recent activity.
- Review new documents and ingestion status.
- Verify invitations and new accounts.
- Confirm no critical errors appear in the UI or logs.

## Weekly Tasks

- Review audit events for sensitive changes.
- Check member records, contributions, and event schedules.
- Verify chat usage and document citations are working.
- Confirm disabled modules are still intentionally disabled.

## Monthly Tasks

- Review backups and restore evidence.
- Rotate credentials where policy requires it.
- Validate module toggles against current business use.
- Review support questions and recurring operational issues.

## Tenant Configuration

The admin should understand these settings:

- branding name, color, and logo URL
- enabled modules
- invitation and user lifecycle
- document access rules
- public versus private visibility for events and announcements

## Admin Overview

The admin landing page should now act as an operations hub:

- summary cards show the live state of documents, audit activity, contributions, and enabled tenant modules
- a watchlist highlights missing setup items or ingestion issues
- the launch-readiness section reuses the onboarding checklist logic
- quick actions should take the admin directly to settings, documents, members, announcements, events, audit, and channel diagnostics when those modules are enabled

## Team Access Operations

Tenant administrators can now manage team onboarding from the admin console:

- use `/admin/access` to invite a teammate with a real tenant-scoped role
- review pending, accepted, cancelled, and expired invitation states in one place
- cancel a pending invitation if the access request is no longer valid
- securely share the acceptance URL when no email delivery integration is configured yet
- use the audit trail to review who created or cancelled invitations

## Upgrade Procedure

1. Take a backup.
2. Read the deployment guide.
3. Apply migrations.
4. Rebuild and redeploy images.
5. Run the production smoke check.
6. Verify a real user journey after restart.

## Incident Triage

If something looks wrong:

1. Check `/health`.
2. Check `/metrics`.
3. Check the admin ingestion health endpoint.
4. Review the audit trail for recent administrative changes.
5. Escalate only after confirming it is not a tenant configuration issue.

## Operating Principle

Administrators can manage the product, but they do not override backend access control. If the backend denies access, the UI must reflect that denial rather than bypass it.
