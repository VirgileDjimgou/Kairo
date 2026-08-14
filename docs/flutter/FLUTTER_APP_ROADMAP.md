# Kairo Flutter Client Roadmap

## Purpose

Create a separate, production-grade Flutter application that reproduces the functional
and visual scope of the Vue 3 PWA while adding Android-native capabilities. The current
PWA stays in production. The Flutter client consumes the same FastAPI contracts and
never takes ownership of backend business rules or authorization.

Initial targets are Android and Flutter Web. iOS and desktop compatibility is designed
in from Sprint F0, but release work for those platforms is deferred until adoption
justifies it.

## Track-Wide Acceptance Rules

- Never use local UI state as a permission decision.
- Every remote record, local cache, and pending command is scoped by authenticated user
  and `tenant_id`.
- No password is stored by the application.
- Finance validation, sanctions, deletion, role changes, and restoration remain online,
  API-authorised operations.
- Each completed sprint updates `PROJECT_STATUS.md` and `FEATURE_PARITY.md`.
- A sprint requires unit/widget tests, relevant API-contract tests, Android and Flutter
  Web builds, and visual evidence at phone and desktop widths.

## Sprint F0 — Foundation, Parity Baseline, And Design System

**Status:** Completed — local Android debug APK and production Flutter Web builds pass.

**Goal:** establish a maintainable Flutter application without changing the PWA.

**Deliverables**

- Flutter project under `apps/flutter_kairo/` with Android and Web enabled;
- development, staging, and production configuration without embedded secrets;
- typed API client foundation and environment-safe API base URL resolution;
- routing, application shell, theme tokens, responsive breakpoints, error boundaries;
- French-first localization with English and German from the first screen;
- design-token comparison with the existing Kairo interface;
- CI skeleton for format, analysis, tests, Android debug build, and Flutter Web build;
- screenshot and parity-evidence directory convention.

**Acceptance:** blank authenticated shell can build for Android and Web, has accessible
theme/localization foundations, and the parity matrix is maintained.

## Sprint F1 — Authentication, Account Security, And Session Boundaries

**Status:** Completed — sign-in, MFA, tenant selection, secure token storage, forced
password replacement, self-service recovery guidance, active-session management and
account-security controls are implemented against the existing API contracts.

**Goal:** reproduce safe access before any protected business screen exists.

**Deliverables**

- login, password visibility toggle, MFA and tenant selection;
- secure token storage, refresh, logout, expired-session recovery, and device identity;
- forced password replacement, self-service password change, and assisted-recovery
  guidance consistent with the existing API;
- account security, active-session inventory and revocation flows;
- role/tenant-aware route guards that remain presentation-only.

**Acceptance:** all canonical roles can authenticate; recovery/session-revocation tests
show no cross-account cached data remains after logout or forced recovery.

## Sprint F2 — Role Shell, Dashboard, And Member Operations

**Status:** Completed — role-aware Android/Web navigation, dashboard and member operations validated against existing API contracts.

**Goal:** establish the everyday association navigation and member workflow.

**Deliverables**

- mobile-first bottom navigation and responsive Web navigation;
- role-aware dashboard cards, inbox entry, loading/retry/empty states;
- progressive member search, list and read-only detail panel;
- authorised member registration, automatic code/email previews, structured address,
  contribution type, immediate-access flow, edit, pause and reactivation;
- confirmation and human-readable operation feedback.

**Acceptance:** president, vice president, secretary, ordinary member and principal
administrator see only API-authorised routes and actions; phone and desktop screenshots
match the documented PWA behaviour.

## Sprint F3 — Contributions, Receipt Declarations, And Treasury Custody

**Status:** Completed — income declaration, personal contribution statement,
treasurer validation/custody, notification inbox, readable operation journal and
authenticated role/visual proof are implemented.

**Goal:** reproduce the core money-receipt workflow without compromising backend control.

**Deliverables**

- member contribution balances, payment history and personal self-view;
- receipt declarations for dues, donations, sponsorship, tournaments and other income;
- progressive/manual source selection with validation feedback;
- treasurer validation/rejection with required reason, configurable handover reminders,
  cashbox confirmation and custody closure;
- role-specific notifications and readable audit status.

**Acceptance:** declaration, validation, rejection and custody lifecycle are proven for
the declaring officer, treasurer, affected member, and an unauthorised role.

## Sprint F4 — Finance Workspace, Expenses, Exports, And Budget Views

**Status:** Completed — treasurer budget/expense controls, auditor read-only finance
visibility, member finance search, reports and Android/Web visual proof are implemented.

**Goal:** complete financial parity for treasurer and auditor.

**Deliverables**

- treasurer and auditor finance workspaces with intelligent member search;
- treasurer-only categorised expense recording with confirmations;
- annual budget summaries and responsive income/expense charts;
- authorised Excel, PDF and share-ready report flows;
- finance audit read-only mode and mobile-friendly action layouts.

**Acceptance:** finance totals match API source data; treasurer-only writes are denied to
other roles by API tests; exported-data and chart states have Android/Web visual proof.

## Sprint F5 — Discipline, Governance, Documents, And Communications

**Status:** Completed — censor discipline workflow, authorised read-only governance
views, recovery-centre visibility, Android/Web evidence and contract-backed role tests
are implemented.

**Goal:** reproduce the governed association workspaces.

**Deliverables**

- discipline workspace with censor write access and president/secretary read-only access;
- searchable disciplinary history with sanctions, amounts, dates, status and context;
- policies, documents, events, announcements and operations journal;
- backup/recovery centre visibility restricted to the existing authorised roles;
- consistent member detail links where permitted.

**Acceptance:** privacy and role boundaries are verified for all disciplinary and
governance views; no data appears for an unauthorised tenant or role.

## Sprint F6 — Chat, AI State, And Notification Inbox Parity

**Status:** Completed — API-backed streamed chat, source citations, safe AI runtime
states, inbox preferences/deep links and Android/Web visual evidence are implemented.

**Goal:** reproduce the optional private-assistant and in-app notification experience.

**Deliverables**

- API-backed chat conversations, streamed answers and source citations;
- AI enabled, disabled, unavailable and deferred-indexing states;
- in-app notification inbox, read state, deep links and preferences;
- operation feedback overlays and human-readable journal outcomes.

**Acceptance:** the Flutter client handles the local-AI-runtime absence gracefully and
does not receive unauthorized citation or notification data.

## Sprint F7 — Offline-First Data, Drafts, And Conflict-Safe Sync

**Status:** Completed — identity-scoped secure cache, safe local drafts, offline
status, cleanup-on-sign-out, Android/Web evidence and network-loss tests are implemented.

**Goal:** deliver useful offline behaviour without offline authorization.

**Deliverables**

- encrypted per-user/per-tenant local cache for permitted read data;
- connectivity banner and explicit last-synchronised state;
- offline drafts for permitted receipt, expense and disciplinary-entry preparation;
- idempotent pending-command queue with retries and replay protection;
- conflict UI, manual refresh and cleanup on logout/session revocation;
- sync contracts and API changes only where required.

**Acceptance:** network-loss and restart simulations preserve drafts without duplicating
server actions; final treasury and discipline decisions remain server-authorised.

## Sprint F8 — Android Native Capabilities

**Status:** Completed — secure device registration, native sharing, document
selection/upload, bounded authentication recovery, explicit Android notification
permission, tenant-scoped FCM delivery, background notification and authenticated
deep-link proof are implemented; see `F8_ANDROID_NOTIFICATIONS.md`.

**Goal:** make Android materially better than a browser wrapper.

**Deliverables**

- Firebase Cloud Messaging registration, preferences and deep-link handling;
- native local reminders for already-authorised actions;
- secure storage, file selection/download, share sheet and attachment capture;
- biometric or device-PIN re-entry if justified by a threat-model review;
- Android permission rationale, denial handling and device-session management.

**Acceptance:** notifications, share flows and sensitive-storage behaviour are proven on
a physical Android device or documented emulator limitations; no API tokens are exposed
to browser-style storage.

## Sprint F9 — Release Readiness, Accessibility, And Controlled Android/Web Launch

**Status:** In progress — release configuration, documentation and regression
verification are being prepared. Android/Cloudflare production promotion is blocked
until a private upload keystore and explicit association approval are supplied.

**Goal:** prepare a controlled release while retaining the PWA as a stable fallback.

**Deliverables**

- complete parity-matrix review and documented intentional differences;
- accessibility, performance, offline, network-failure and security regression suite;
- Android app signing, package identity, versioning and Play Console test-track assets;
- Flutter Web deployment configuration behind the existing Cloudflare architecture;
- release notes, operator guide, privacy disclosures and support procedure;
- pilot feedback loop and rollback plan to the PWA.

**Acceptance:** Android internal testing package and Flutter Web staging release are
validated with canonical roles, tenants, phone widths and desktop widths. A production
promotion requires explicit user approval.

## Deferred After F9

iOS and desktop are separate delivery decisions, not hidden work in the Android/Web
roadmap. When promoted, each receives its own sprint with platform hardware, signing,
store/distribution, accessibility and notification validation.

## Post-Roadmap Stabilisation — Visual Redesign

**Status:** Completed.

The Flutter Android/Web client received a complete Material 3 visual redesign after
the functional sprints. It is a presentation-only stabilisation: it introduces shared
light/dark themes, semantic design tokens, responsive cards, state panels, status
badges and mobile-first workspace layouts without changing API contracts, FastAPI
policy enforcement, tenant boundaries or the Vue 3 PWA. The evidence and design audit
are maintained in `docs/FLUTTER_VISUAL_REDESIGN_REPORT.md` and
`docs/FLUTTER_UI_AUDIT.md`.
