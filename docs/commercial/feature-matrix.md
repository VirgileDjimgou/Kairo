# Feature Matrix

This matrix helps explain what is included in the current product and what is optional or future-oriented.

## Core Modules

| Module | Status | Notes |
|---|---|---|
| Identity and tenancy | Included | JWT auth, tenant switching, invitations, password reset, MFA scaffold |
| Documents and ingestion | Included | Upload, OCR, archive, bulk upload, retry, diagnostics |
| RAG chat | Included | Permission-aware retrieval, citations, refusal behavior |
| Membership | Included | Profiles, self-view, admin management |
| Contributions | Included | Records, balances, payments, export/import |
| Policies | Included | Public member view and admin management |
| Disciplinary | Included | Private records with role controls |
| Events | Included | Member view and admin CRUD |
| Announcements | Included | Visibility-aware publishing |
| Audit trail | Included | Sensitive action logging and review |
| Settings | Included | Branding and module toggles |
| Observability | Included | `/health`, `/metrics`, request IDs, ingestion health |
| Guided onboarding | Included | Dashboard checklist and setup-oriented empty states |

## Optional Channels

| Channel | Status | Notes |
|---|---|---|
| Email | Placeholder | Provider abstraction only |
| Telegram | Placeholder | Provider abstraction only |
| WhatsApp | Placeholder | Provider abstraction only |

## Future Premium Or External Integrations

| Area | Status | Notes |
|---|---|---|
| Enterprise SSO | Future | Not part of the current delivery baseline |
| Real gateway integrations | Future | Notification providers are simulated today |
| Managed hosting | Offer choice | Operational model, not a code change |
| Dedicated onboarding | Offer choice | Can be added as a service package |

## Commercial Reading

- Everything marked "Included" is present in the product and validated by tests or builds.
- Everything marked "Placeholder" is safe to mention only as optional groundwork.
- Everything marked "Future" should not be sold as already complete.
