# Flutter Client Project Status

Last updated: 2026-08-14

## Track Purpose

Build a separate Kairo Flutter client that reproduces the authorised functional and
visual behaviour of the existing Vue 3 PWA while adding a reliable native Android
experience, offline capability, native sharing, and native notifications.

The Vue 3 PWA remains the production client throughout this track.

## Current Sprint

Flutter Sprint F9 — Release Readiness, Accessibility, And Controlled Android/Web Launch

Status: In progress — controlled release configuration is implemented without changing
the production Vue PWA. Android release signing deliberately fails closed until the
association supplies its private upload keystore. Flutter Web has a separate staging
Docker configuration and requires an explicit Cloudflare hostname before it is public.

## Official Next Action

Complete F9 verification, then request explicit approval before any Flutter Android or
Cloudflare production promotion.

## Sprint F0 Evidence

- Flutter 3.44.9 installed in the local development tools directory;
- `flutter analyze` passes with no issue;
- `flutter test` passes: configuration safety plus mobile and desktop widget layouts;
- production Flutter Web build passes with `KAIRO_API_BASE_URL` set to the public API;
- visual validation passed at 390 × 844 (Android phone layout) and 1280 × 900
  (desktop Web layout); see `apps/flutter_kairo/artifacts/sprint-f0/README.md`;
- local Android debug APK validation passes at
  `apps/flutter_kairo/build/app/outputs/flutter-apk/app-debug.apk`; Android SDK
  command-line tools are available. Flutter doctor still reports unaccepted optional
  SDK licences, which do not block the tested debug build.

## Sprint F1 Evidence

- API-backed sign-in supports e-mail, phone number and username identifiers through the
  existing FastAPI endpoint;
- password visibility control, MFA challenge completion/enrolment, tenant selection,
  forced initial-password replacement, password change and recovery guidance are implemented;
- active-session inventory, individual revocation, other-session revocation and
  full-session termination are implemented through the existing API contracts;
- only the access token is stored through `flutter_secure_storage`; passwords and MFA
  challenges are never persisted;
- `flutter analyze` and all 10 Flutter tests pass;
- production Flutter Web build and Android debug APK build pass.

## Sprint F2 Evidence

- Role-aware mobile bottom navigation and responsive Web navigation are implemented;
- role-aware dashboard, resilient directory loading, empty/error states and member detail panel are implemented;
- member search, creation, edit, pause and reactivation use the existing FastAPI membership API contracts;
- member creation includes server-owned member code/e-mail generation, German structured address, membership type and optional immediate-access input;
- president directory/navigation and ordinary-member route exclusion are covered by widget tests;
- `flutter analyze` and all 13 Flutter tests pass;
- Android debug APK and production Flutter Web build pass after the F2 implementation.

## Sprint F3 Evidence

- authorised office roles can declare member contributions, donations, sponsorship,
  tournament proceeds and other income through the existing receipt-declaration API;
- member contributions use the backend-provided progressive member-option endpoint;
- the treasurer workspace shows the API review queue and supports explicit validation,
  rejection with a required reason, reminder adjustment (one to seven days), and final
  cashbox-receipt confirmation;
- the automated F3 controller test proves the validated-to-custody lifecycle through a
  fake API gateway; all 17 Flutter tests pass;
- Android debug APK and production Flutter Web builds pass after the F3 increment;
- the authenticated shell now includes the API-backed personal contribution statement,
  notification inbox (including read state), and an office-only human-readable operations
  journal; all responses remain tenant- and role-filtered by FastAPI.
- role-boundary widget tests prove that a president can access the member, receipt and
  journal surfaces, while an ordinary member only receives their personal contribution
  statement and notifications, with no directory, receipt-declaration or journal route;
- visual regression evidence is maintained at
  `apps/flutter_kairo/artifacts/sprint-f3/member-android-contributions.png`,
  `apps/flutter_kairo/artifacts/sprint-f3/president-android-journal.png`, and
  `apps/flutter_kairo/artifacts/sprint-f3/treasurer-web-custody.png`.

## Sprint F4 Evidence

- the Flutter finance workspace consumes the established contribution summary,
  contribution listing, member-finance history, annual-budget, expense and export API
  contracts; no finance calculation or permission is reimplemented locally;
- treasurer UI includes annual income/expense budget breakdowns, categorized expense
  entry with confirmation, recent expense history and Excel/PDF/share-ready exports;
- auditor UI exposes searchable contribution visibility and export controls in read-only
  mode; it never renders the expense-entry surface;
- finance workspace tests cover the treasurer and auditor boundaries; all 21 Flutter
  tests pass and `flutter analyze` has no issues;
- Android debug APK and production Flutter Web builds pass;
- visual regression evidence is maintained at
  `apps/flutter_kairo/artifacts/sprint-f4/treasurer-android-budget.png` and
  `apps/flutter_kairo/artifacts/sprint-f4/auditor-web-read-only.png`.

## Sprint F5 Evidence

- governance tabs consume the established disciplinary, policy, document, event,
  announcement and recovery API contracts; tenant isolation and authorisation remain
  entirely server-enforced;
- the censor receives searchable tenant disciplinary records and a confirmed record-
  creation flow; the president and secretary are presented read-only disciplinary
  information, matching their existing backend permissions;
- every authorised role can consult only the API-visible policies, documents, events
  and announcements; no Flutter route expands a role's access;
- the backup centre is visible only to the existing recovery-authorised roles and
  queues a confirmed backup request without handling archive or encryption secrets on
  the client;
- all 25 Flutter tests pass, `flutter analyze` has no issues, and Android debug plus
  production Flutter Web builds pass;
- visual regression evidence is maintained at
  `apps/flutter_kairo/artifacts/sprint-f5/censor-android-discipline.png` and
  `apps/flutter_kairo/artifacts/sprint-f5/president-web-read-only.png`.

## Sprint F6 Evidence

- the Flutter assistant uses only the authenticated FastAPI chat contract: domain
  policy, conversations, server-sent answer stream and server-filtered citations;
  it never connects directly to the private AI runtime, Ollama or Qdrant;
- streamed assistant text and source citations are rendered in the conversation;
  disabled (`403`) and temporarily-unavailable (`503` and runtime stream error)
  states have clear, safe user-facing recovery UI;
- the inbox now consumes server-owned target paths, read state and preferences;
  notification taps open the matching authorised Flutter workspace, while FastAPI
  remains responsible for the actual permission check;
- notification preferences cover push delivery, finance, discipline, events and
  announcements. Native push registration remains deliberately deferred to F8;
- focused F6 tests cover streamed citations, runtime failure states, preference
  persistence and deep-link dispatch. `flutter analyze` passes with no issue;
- visual-regression evidence is maintained at
  `apps/flutter_kairo/artifacts/sprint-f6/android-private-assistant.png` and
  `apps/flutter_kairo/artifacts/sprint-f6/web-notification-inbox.png`.

## Sprint F7 Evidence

- the secure local workspace is scoped by authenticated user and tenant; scope keys
  do not expose raw identities and every scope is cleared on sign-out;
- authorised `GET` payloads are cached only after a successful API response and can
  be read during a network failure; remote FastAPI authorisation remains the source
  of truth when connectivity returns;
- receipt-declaration and treasurer-expense forms restore local drafts and remove a
  draft only after a successful API operation. No payment, sanction, deletion, role
  action or treasury decision is finalized offline;
- offline status, last synchronisation and queued-draft count are visible in the
  authenticated Android/Web shell;
- F7 tests prove tenant isolation, draft replacement without duplicate queued intent,
  scope cleanup, offline cache lookup and identity-safe keys. The full Flutter suite
  passes with 37 tests; `flutter analyze`, Android debug APK and production Flutter
  Web builds pass;
- visual regression evidence is maintained at
  `apps/flutter_kairo/artifacts/sprint-f7/android-offline-draft.png` and
  `apps/flutter_kairo/artifacts/sprint-f7/web-sync-status.png`.

## Sprint F8 Evidence

- authentication and profile requests have a 20-second upper bound; transport and
  unexpected failures clear any partial session and return to the sign-in screen with
  an explicit service-unavailable message instead of an indefinite white spinner;
- the production Android APK and Flutter Web release build both target
  `https://app.combissportverein.org/api/v1`;
- Android notification permission, FCM token registration, generic background push
  delivery while the app is not visible, and authenticated deep-link dispatch into
  the finance workspace were exercised against the deployed FastAPI service;
- a single device can retain distinct tenant/user notification profiles; preference
  updates are applied consistently to every registered device profile for that user;
- real-API Android dashboards were captured for secretary general, auditor, censor,
  sports manager, vice president, administrator and treasurer. The compact navigation
  renders at most five destinations and uses the short mobile label `Caisse`;
- `flutter analyze` reports no issue, all 42 Flutter tests pass, Android debug APK and
  production Flutter Web builds pass, and all 303 API tests pass;
- a physical Samsung SM-G975F was connected through ADB for the final confirmation:
  notification activation, background FCM delivery and the authorised deep link back
  into the application are captured under
  `apps/flutter_kairo/artifacts/sprint-f8/physical-device/`.

## Sprint F9 Evidence

- application version is `1.0.0+2`; package identity remains
  `org.combissportverein.kairo` to preserve Android/Play continuity;
- release Gradle configuration no longer falls back to debug signing. A private upload
  keystore and ignored `android/key.properties` are required for an AAB;
- `apps/flutter_kairo/scripts/release_check.ps1` runs format, analysis, tests, Flutter
  Web release and Android debug package verification. The optional AAB step verifies
  the signing gate but never deploys;
- `docker-compose.flutter-web.yml` and the Flutter Web Nginx gateway create a separate
  staging service with same-origin `/api/` proxying. It does not alter the PWA service
  or the existing Cloudflare route;
- static verification is clean (`flutter analyze`), all 43 Flutter tests pass, the
  staging Flutter Web build and Android debug APK build pass, and the Nginx and merged
  Docker Compose configurations validate successfully;
- an unsigned release-bundle attempt fails explicitly with the required-keystore
  message, proving release signing cannot silently fall back to debug credentials;
- phone and desktop sign-in regression baselines are maintained in
  `apps/flutter_kairo/artifacts/sprint-f9/`, including semantic checks for the
  password-visibility action;
- release notes, Android/Web runbook, privacy/support procedure and a pilot-feedback
  form are available in `docs/flutter/`;
- permanent member deletion is recorded as an intentional pilot deferral in
  `FEATURE_PARITY.md`; the PWA remains the role-gated fallback for that destructive
  operation.

## Visual Redesign Programme — Phase 1

- the Flutter-only Material 3 design foundation is in progress and documented in
  `docs/FLUTTER_UI_AUDIT.md` and `docs/FLUTTER_VISUAL_REDESIGN_REPORT.md`;
- shared tokens, semantic light/dark themes and reusable application surfaces are
  implemented without changing FastAPI contracts, permissions or the Vue 3 PWA;
- the authenticated shell, dashboard and profile now consume the new system. The
  remaining feature workspaces are being migrated progressively with responsive and
  accessibility verification.

## Release Targets

| Target | Status | Scope |
| --- | --- | --- |
| Android | Primary | First installable release and Play Store preparation |
| Flutter Web | Primary | Browser-accessible companion application |
| iOS | Deferred | Architecture-ready, no release commitment yet |
| Desktop | Deferred | Architecture-ready, no release commitment yet |

## Non-Negotiable Constraints

- FastAPI remains the source of truth for roles, permissions, tenant isolation, finance,
  discipline, audit, and validation.
- No Flutter feature is considered complete until its matching PWA capability is tracked
  in `FEATURE_PARITY.md`.
- Offline data and queues must be per-user and per-tenant, encrypted where supported,
  and cleared when a session is revoked or signed out.
- Only Android and Flutter Web may receive release-specific work before a roadmap update.

## Handoff Command

```text
Continue Next Sprint Implementation Flutter App
```
