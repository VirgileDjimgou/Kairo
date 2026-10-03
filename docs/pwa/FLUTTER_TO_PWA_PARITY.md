# Flutter → PWA Parity Matrix And Freeze Register

Status: Active — Roadmap V2 Sprint 119
Decision: `docs/architecture/decisions/0014-pwa-first-flutter-frozen.md`

This document inventories the capabilities delivered by the Flutter client
(`apps/flutter_kairo/`, sprints F0–F9 plus the visual redesign) and classifies
each one for the PWA-first program S119–S128:

- **Available** — the Vue 3 PWA already provides the capability.
- **Planned S120–S124** — the capability is a committed task of an active sprint.
- **Deprecated** — the capability is intentionally not carried into the PWA; the
  decision and its rationale are recorded here.

Flutter is frozen as legacy/reference code: it receives no new business features,
is not a blocking job of the default release pipeline, and is not deleted during
S119–S128. Flutter source may be consulted for behavior, notification and parity
reference only.

## Client ownership

| Client | Role | Release pipeline | Change policy |
| --- | --- | --- | --- |
| Vue 3 PWA (`apps/web/`) | Canonical, supported client | Blocking: Security, API, Contracts, Web, Production | Active development |
| Flutter (`apps/flutter_kairo/`) | FROZEN / LEGACY REFERENCE | Optional/manual (`flutter-legacy` workflow) | No new business features; reference only |
| FastAPI (`services/api/`) | Sole policy enforcement point | Blocking: Security, API, Contracts | Active development |

## Capability inventory

| # | Capability (Flutter origin) | PWA status | Classification | Notes |
| --- | --- | --- | --- | --- |
| 1 | Material 3 theme, responsive phone/desktop shell | Vue design system + responsive layouts | Available | Both clients already share the semantic design language (S103). |
| 2 | FR/EN/DE localization from the first screen | Feature catalogs under `apps/web/src/i18n/{fr,en,de}` | Available | Parity enforced by `check-i18n-parity.mjs`. |
| 3 | Login, password visibility, MFA, tenant selection, forced password change | `views/auth/**`, `stores/auth.store.ts` | Available | Same API contracts. |
| 4 | Session inventory and revocation | Account security views | Available | Same API contracts. |
| 5 | Role-aware dashboard and navigation | Router views + capability-driven navigation | Available | ADR-008. |
| 6 | Member directory, registration, edit, pause/reactivate, detail panel | `views/members/**` | Available | Same API contracts. |
| 7 | Permanent member deletion (role-gated) | President/secretary PWA workflow | Available | Flutter deferred it; the PWA remains the controlled fallback (`docs/flutter/FEATURE_PARITY.md`). |
| 8 | Contributions, receipts, treasurer validation, custody, expenses, budgets, exports | `features/finance/**` | Available | Same API contracts. |
| 9 | Discipline workspace (censor write, executive read-only) | `views/disciplinary/**` | Available | Same API contracts. |
| 10 | Governance, documents, policies, journal, backup/recovery centre | `views/governance/**`, `views/admin/**` | Available | Same API contracts. |
| 11 | Private assistant with streamed answers and citations | `views/chat/**` | Available | Same API contracts; retrieval filtering is server-owned. |
| 12 | In-app notification inbox, read state, preferences | `components/ui/NotificationBell.vue`, notifications views | Available | Same API contracts. |
| 13 | Standards-based Web Push (VAPID) | `services/web-push.ts` + `src/sw.ts` | Available | Flutter Web intentionally had none; the PWA owns browser push. |
| 14 | Android FCM registration and background/terminated delivery | — | Planned S121 | Requires the normalized installation model and Firebase Web Messaging registration (S120 worker + S121 registration). |
| 15 | Push permission UX after meaningful interaction | Partial (explicit enable action) | Planned S124 | S124 forbids requesting permission on first visit and defines the enablement journey. |
| 16 | Notification click → exact authorized target route | Partial: `safeTarget()` allowlists same-origin paths; open windows use full navigation | Planned S120, S122 | S120 defines the `SERVICE WORKER → NAVIGATE(targetPath) → VUE ROUTER` contract; S122 adds capability verification and inbox fallback. |
| 17 | Native share sheet (F8) | Finance exports use download/print/WhatsApp deep links | Deprecated | Not planned in S120–S124. Web Share API coverage is inconsistent on desktop browsers; the PWA keeps explicit download and share-target flows. Reconsider only if a roadmap decision promotes it. |
| 18 | File selection, upload, download (F8) | Standard `<input type="file">` upload and authenticated downloads | Available | Browser-native behavior covers the workflow. |
| 19 | Secure session storage (`flutter_secure_storage`) | Access token in browser storage + authenticated API session | Available | Browser model differs by design; the PWA is the canonical client and the backend remains the enforcement point. No password is stored. |
| 20 | Bounded authentication recovery (20 s timeout, clear partial session) | Session/error handling in auth store and API client | Available | Same recovery behavior expected from the PWA. |
| 21 | Authenticated read cache scoped by user/tenant (F7) | — | Deprecated | The PWA does not carry an authenticated data cache during S119–S128; S120 provides the offline app-shell strategy and authenticated operations require connectivity. |
| 22 | Offline drafts and queued safe commands (F7) | — | Deprecated | Draft/queue behavior was a Flutter-only native convenience; it is not part of the PWA program. The backend still owns idempotency and validation. |
| 23 | Logout/session revocation of push binding | `revokeCurrentDevice()` on sign-out | Available | S121 extends this to the normalized installation model. |
| 24 | Multi-account push profiles on one installation | Backend supports multiple profiles per installation (S114) | Planned S121 | S121 must prove no cross-account push leakage on one browser installation. |
| 25 | Biometric/device-PIN re-entry | — | Deprecated | Never implemented in Flutter either; no active roadmap commitment. |
| 26 | Android Play Store packaging and signing | — | Deprecated | The Flutter release track is closed. PWA installability is delivered by S124 instead. |
| 27 | Flutter Web staging service | — | Deprecated | `docker-compose.flutter-web.yml` and the Flutter Nginx gateway are preserved for reference only; they are not part of the PWA release path. |
| 28 | Tenant branding in launcher/notification identity | Partial: tenant branding exists for the in-app shell | Planned S123, S124 | S123 defines `TenantBranding`; S124 applies it to manifest, icons, name and theme. |

## Notification and deep-link gap register (S120–S124)

| Gap | Description | Owner sprint | Status |
| --- | --- | --- | --- |
| G1 | Firebase Web Messaging background handler inside the canonical Service Worker (in addition to VAPID Web Push). | S120 | Closed in S120 (`src/sw.ts`, `onBackgroundMessage`; registration and token lifecycle remain S121) |
| G2 | Exactly one Service Worker controls the origin/scope; verify no competing registration from legacy code. | S120 | Closed in S120 (`npm run pwa:check` + built-worker Playwright test) |
| G3 | `SERVICE WORKER → NAVIGATE(targetPath) → VUE ROUTER` contract: in-app navigation for an already-open client instead of a full page reload where possible. | S120 | Closed in S120 (`src/services/pwa-navigation.ts`, `postMessage` contract) |
| G4 | Click behavior verified for app open, backgrounded, closed, multiple tabs, standalone PWA and browser window. | S120, S128 | Partially closed in S120 (open/closed window focus and openWindow paths tested); S128 prepared the Chrome Android checklist (`docs/pwa/COMBIS_PILOT_CHECKLIST.md`) and validated the browser deep-link target against the real stack — multi-tab/standalone real-device validation stays PENDING until an operator records it |
| G5 | Normalized browser installation model (`status`, browser/device metadata, `last_seen_at`, `revoked_at`) beyond the current subscription record. | S121 | Closed in S121 (migration 0034, `docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`) |
| G6 | FCM web token registration, renewal and invalid-token cleanup through the same installation identity; retry telemetry. | S121 | Closed in S121 (Firebase Web Messaging fallback, token rotation, retry counters in notification health) |
| G7 | Tenant switching and logout revoke only the matching profile binding; no cross-tenant or cross-account leakage. | S121 | Closed in S121 (revoke-before-switch, multi-profile safety, tenant-isolation tests) |
| G8 | Click target verification: authentication → tenant → capability → resource authorization; fall back to the authenticated inbox when the target is inaccessible (currently falls back to the dashboard). | S122 | Closed in S122 (client route validation + inbox fallback; ADR-015) |
| G9 | Client-side internal route allowlist/validation aligned with the backend deep-link contract. | S122 | Closed in S122 (backend `deep_links.py` allowlist + client router validation) |
| G10 | Privacy-safe payload verification for payment, contribution, receipt, cash handover, treasury confirmation, expense, announcement, event, disciplinary and administrative cases. | S122 | Closed in S122 (representative-case tests assert generic push payloads and exact targets) |
| G11 | Tenant-aware manifest, application name, short name, icons, maskable icon, theme and background colors. | S123, S124 | Closed in S123/S124 (canonical `TenantBranding` + public tenant manifest endpoint with absolute icons and defaults) |
| G12 | Installation UX (`beforeinstallprompt`, custom CTA, `appinstalled`, standalone detection, fallback guidance, post-install onboarding) without aggressive permission prompts. | S124 | Closed in S124 (`pwa-install.ts` + `InstallAppPrompt.vue`; installation never requests notification permission) |

## Reference-only Flutter assets

These remain in the repository as legacy reference and are not maintained as
active deliverables:

- `apps/flutter_kairo/` — full source tree, tests and artifacts;
- `docs/flutter/**` — F0–F9 history, parity matrix, runbooks, pilot material;
- `prompts/FLUTTER_CONTINUE_UNIVERSAL.md` — closed continuation prompt;
- `.github/workflows/flutter-legacy.yml` — manual Flutter verification only.

## Exit condition

Flutter is not deleted during S119–S128. After S128, archival can be considered
only when PWA installability, background/closed push, deep-link parity and the
COMBIS pilot are validated and no required Flutter-only workflow remains. Any
removal is a separate explicit change outside this roadmap.
