# Flutter Feature Parity Matrix

This matrix prevents a visual-only rewrite. Every feature must be reproduced with its
server-enforced permissions, error behaviour, responsive layout, and relevant role
coverage before the Flutter client is considered a replacement for that surface.

Status values: `Planned`, `In progress`, `Verified`, `Deferred`.

| Domain | Required Flutter capability | Key roles | Functional parity | Visual parity | Status |
| --- | --- | --- | --- | --- | --- |
| Foundation | Theme, routing, French/English/German, responsive Android/Web shell | All | Required | Required | Verified |
| Authentication | Login, password visibility, session handling, MFA, forced password change | All | Required | Required | Verified |
| Account security | Password change, assisted recovery guidance, devices and session revocation | All / authorised officers | Required | Required | Verified |
| Dashboard | Role-aware landing pages, loading and recovery feedback | All | Required | Required | Verified |
| Members | Search, registration, edit, pause/reactivate and detail panel | President, VP, secretary, offices | Required | Required | Verified |
| Member deletion | President/secretary role-gated deletion confirmation | President, secretary | Required | Required | Deferred |
| Contributions | Individual/family dues, balances, payment history and self-view | Member, treasurer, auditor | Required | Required | Verified |
| Receipts | Member and non-member income declarations, pending queue, validation/rejection | Office roles, treasurer | Required | Required | Verified |
| Custody | Handover reminders, receipt confirmation, closure trail | Treasurer, declarant | Required | Required | Verified |
| Expenses and budgets | Treasurer expense entry, categories, budget cards, exports and charts | Treasurer, auditor | Required | Required | Verified |
| Discipline | Read/write boundaries, record history, sanctions and payment state | Censor, president, secretary, member | Required | Required | Verified |
| Governance | Documents, policies, operations journal, backup/recovery centre | Authorised office roles | Required | Required | Verified |
| Communication | Events, announcements, notification inbox and preferences | Authorised roles | Required | Required | Verified |
| Chat and AI | Optional private assistant, citations, disabled/unavailable states | Roles permitted by API | Required | Required | Verified |
| Native capabilities | Android device registration, sharing, files, secure storage, FCM registration, background delivery and authenticated deep links | Android users | Required | Required | Verified |
| Offline sync | Cached read data, drafts, queued safe actions, conflicts and recovery | Authorised roles | Required | Required | Verified |
| Release quality | Accessibility, performance, error monitoring, Android/Web deployment evidence | All | Required | Required | In progress |

## F9 Controlled-Pilot Review

All rows marked `Verified` have the existing Android/Web build, role and visual
evidence recorded in `docs/flutter/PROJECT_STATUS.md` and the matching sprint artifact
directory. The remaining differences are intentional and do not grant a Flutter user
additional authority:

- **Permanent member deletion** is deferred from the first Flutter pilot. The existing
  role-gated PWA workflow remains the controlled fallback for the president and
  secretary general.
- **iOS and desktop distribution** remain deferred after F9; Android and Flutter Web
  are the only release targets.
- **Flutter Web is staging-only** until an authorised operator explicitly promotes a
  new Cloudflare hostname. The existing PWA hostname is never overwritten by this
  configuration.

## Verification Evidence Per Row

For each `Verified` row, record in the sprint evidence:

- Android emulator or physical-device proof;
- Flutter Web proof at desktop and phone widths;
- role and tenant test evidence;
- offline/error-state evidence when applicable;
- links or paths to maintained screenshots and test reports.
