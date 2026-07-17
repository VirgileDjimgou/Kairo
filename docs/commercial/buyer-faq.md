# Buyer FAQ

This FAQ is written for association boards, administrators, and evaluators who are not expected to read the full technical documentation first.

## What is Kairo in simple terms?

Kairo is a private management platform for an association or organization. It combines member administration, documents, contributions, announcements, events, and a controlled AI assistant in one workspace.

## Is the AI allowed to see everything?

No. The backend decides what a user is allowed to access before the AI receives any source material. The AI does not decide permissions on its own.

## Can an ordinary member see another member's data?

No. Ordinary members stay in a read-first experience focused on their own information and public association material.

## Which roles are supported?

The current role track covers:

- `member`
- `secretary_general`
- `treasurer`
- `auditor`
- `censor`
- `sports_manager`
- `president`
- `vice_president`
- `principal_admin`

## Does Kairo support multiple organizations?

Yes. Kairo is multi-tenant. Each organization stays isolated, and the backend enforces that isolation.

## Can it be self-hosted?

Yes. The repository and deployment runbooks support self-hosting with Docker Compose.

## Is there a managed-service option?

Yes, as a service model. That option depends on an operational agreement and is not just a code toggle.

## Does Kairo already include backups and rollback guidance?

Yes. The current packaging includes documented and scripted preflight, install, upgrade, backup, restore, rollback, and smoke-validation flows.

## Are email, Telegram, and WhatsApp fully equivalent today?

No. Email is the real delivery path for identity workflows such as invitations and password reset. Telegram and WhatsApp are now both available as real operator notification paths when their respective provider settings are configured. They are still not fully equivalent because WhatsApp currently depends on an external gateway contract and none of the live channels yet exposes provider-side webhook reconciliation.

## Is Kairo ready for a large enterprise rollout?

Not as a generic enterprise platform. The current positioning is stronger for associations, clubs, NGOs, and similar organizations that want a professional but controlled deployment.

## What still needs to be decided outside the code?

Typical non-code decisions still include:

- hosting model
- support hours and SLA wording
- legal terms
- data processing agreements if required
- branding and pricing
