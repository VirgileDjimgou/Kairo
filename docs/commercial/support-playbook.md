# Support Playbook

This playbook defines the support boundary for Kairo.

## Support Scope

Included in standard support:

- installation and upgrade guidance
- application configuration
- backup and restore procedures
- document ingestion troubleshooting
- login, invitation, and password reset issues
- tenant settings, module toggles, and admin workflow questions

Not included by default:

- customer-specific infrastructure outages
- third-party gateway outages
- custom plugin development
- data recovery from backups that were never created
- legal or compliance sign-off

## Severity Triage

### Severity 1

- service unavailable
- data exposure risk
- broken authentication across tenants

### Severity 2

- major module is unavailable
- restore or upgrade fails
- repeated ingestion failures

### Severity 3

- single workflow degraded
- documentation gap
- minor UI or reporting issue

## Standard Diagnosis Order

1. Verify `/health`.
2. Verify `/metrics`.
3. Check the admin ingestion health endpoint.
4. Review recent audit events.
5. Check container logs.
6. Reproduce on a fresh stack if needed.

## Common Questions

### Why is a module missing from the menu?

The tenant may have it disabled in settings, or the user may not have the required role.

### Why does the chat refuse to answer?

The system may have no approved source for the answer, or the query may touch data the user is not allowed to see.

### Why do we need a backup before upgrade?

Because the product is designed to be recoverable and upgrades must preserve tenant-scoped data.

## Escalation Rule

If the issue could involve tenant isolation, unauthorized access, or data loss, escalate immediately and preserve evidence before making changes.
