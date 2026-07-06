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
- Open the tenant settings page and refresh the recovery evidence timestamps after a real backup or restore drill.
- Watch for the recovery evidence badge in the admin overview:
  - `healthy` means the evidence is current and the alert posture is configured
  - `warning` means the proof is aging or incomplete
  - `critical` means backup or restore proof is missing, or alert contacts are not configured
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
- review the delivery outcome after each invitation; real email delivery now hides the secure link from the UI on successful production dispatch
- securely share the acceptance URL only when the provider is in simulation mode or delivery failed and manual fallback is required
- use the audit trail to review who created or cancelled invitations

## User Lifecycle Controls

Tenant administrators can now use `/admin/access` for containment and offboarding as well:

- review the current membership state of tenant users
- suspend a user when access must be stopped immediately for the current tenant
- reactivate a previously suspended user without creating a new invitation
- revoke active tenant sessions for a managed user during incident response
- rely on backend enforcement: suspended memberships lose access even if a stale token still exists in the browser

## Account Security Expectations

User-facing security is now partly self-service:

- signed-in users can open `/account/security` to review MFA status and complete MFA setup
- signed-in users can review active sessions, revoke stale sessions, and force a logout of all sessions from the same security screen
- users can disable MFA from the authenticated shell if policy allows it
- signed-in users can trigger the backend password recovery flow against their own email from the product shell
- password reset and session revocation actions are now visible in the audit trail for identity incident review
- administrators should still treat backend policy as the authority and use the audit trail for sensitive identity actions

## Identity Recovery Expectations

- expired invitation links fail safely and should result in a fresh invitation rather than a manual workaround
- already-used or expired password reset links must be replaced with a newly generated reset flow
- users with suspended or disabled access should see a clear denial state and must not be re-enabled through stale browser state
- MFA completion for users with multiple organization memberships should return them to an organization-selection step before normal navigation resumes
- refresh-token continuity is valid only while the active session still belongs to an active tenant membership

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
