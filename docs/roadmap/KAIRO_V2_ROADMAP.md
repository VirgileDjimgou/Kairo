# Kairo Roadmap V2 — Sprint 100 To Sprint 128

Status: COMPLETE — Sprints 100–128 delivered (canonical V2 record)

This roadmap is the single active execution source for Kairo after the historical
Sprint 0–99 track. The historical record remains in `IMPLEMENTATION_ROADMAP.md` and is
read-only for planning purposes.

Machine-readable companion: `docs/roadmap/KAIRO_V2_ROADMAP.json`.
Execution policy: `docs/automation/SPRINT_BATCH_AUTOPILOT.md`.

Sprints 100–128 are complete. The **S119–S128 program (PWA-first, white-label
SaaS)** closed with Sprint 128: the real full-stack release gate validated the
integrated platform against a deterministic production-like stack and the COMBIS
Chrome Android pilot checklist was prepared (`docs/pwa/COMBIS_PILOT_CHECKLIST.md`).
The Vue 3 PWA is the canonical client; the Flutter client is frozen as
legacy/reference code and receives no new business features. Any further product
work is a new planning decision (see `docs/roadmap/KAIRO_V3_ROADMAP.md`).

Objective: **CONSOLIDATE → PWA → NOTIFICATIONS → WHITE-LABEL → RELIABILITY → HARDEN → RELEASE**.

Constraints that apply to every sprint:

- preserve tenant isolation, backend-owned permissions, capability enforcement, audit
  integrity and transaction correctness;
- preserve the modular monolith (no microservices, no Kafka);
- the Vue 3 PWA is the canonical client; Flutter is frozen as legacy/reference code,
  receives no new business features and must not block the default release pipeline;
- white-label branding, domains, manifests and notification identity come from tenant
  configuration, never from hardcoded product logic;
- authorization remains server-owned; PWA manifests, Service Workers, notification
  payloads, Firebase topics and client role checks are never security boundaries;
- preserve API backward compatibility unless a migration is explicitly planned;
- never expose finance or disciplinary detail through push notifications;
- retrieval authorization must happen before prompt assembly;
- the LLM never decides access control and no frontend grants access;
- no tenant-scoped query may omit `tenant_id`;
- no COMBIS-specific product hardcoding;
- no destructive/remote operations without explicit human approval.

---

## Sprint 100 — Green Engineering Baseline

Phase: STABILIZE. Dependencies: none.

**Goal:** Restore Kairo to a trustworthy engineering baseline before adding new
architecture. Known issues include failing CI in API, Web, Flutter and sensitive-file
checks.

**Tasks**

- Fix current Ruff violations properly.
- Run mypy after Ruff succeeds.
- Run the backend test suite.
- Fix the current Web localization regression.
- Run the broader Web Playwright matrix.
- Fix Flutter test failures and golden regressions. Do not blindly update goldens if
  the rendered change is unintentional.
- Make golden execution deterministic across local and CI environments.
- Fix the sensitive-file scanner false positives: source directories named `backup`
  or `export` must not be treated as backup archives.
- The scanner must still reject actual database dumps, backup archives, member
  exports, financial exports, spreadsheets containing operational data and
  secret-bearing files.
- Verify GitHub Actions logic. Do not weaken CI.

**Acceptance**

- API lint passes; API mypy passes; API tests pass.
- Web type-check, build, localization tests and role/security regressions pass.
- Flutter analyze, tests and relevant builds pass.
- Sensitive file scanner passes without weakening policy.
- No known main-branch regression remains hidden by skipped downstream steps.

---

## Sprint 101 — Repository Privacy And Data Hygiene

Phase: STABILIZE. Dependencies: 100.

**Goal:** Make the source repository safe to publish and clone.

**Tasks**

- Audit the repository for real association documents and operational data
  (including `Combis Sport Verein/`).
- Treat real association documents as operational data, not source code.
- Remove such files from the CURRENT tracked tree when confirmed private.
- Replace required development material with fictional fixtures.
- Strengthen the sensitive file policy to cover operational document classes.
- Document where real operational documents belong: MinIO/S3/private tenant storage.
- Generate a Git history exposure report.
- Prepare exact remediation instructions/scripts; mark remote-history rewriting
  HUMAN_REQUIRED. Never rewrite remote history automatically.

**Acceptance**

- Current HEAD contains no confirmed real tenant operational documents.
- Development fixtures are fictional.
- Security scanner covers operational document classes.
- History remediation report exists.
- No remote history is rewritten automatically.

---

## Sprint 102 — Architecture Truth And Documentation Reset

Phase: STANDARDIZE. Dependencies: 101.

**Goal:** Reduce documentation entropy so agents can determine the next sprint
deterministically.

**Tasks**

- Create a concise current architecture snapshot.
- Create or update architecture decision records.
- Separate historical roadmap, current product state, active roadmap, operator docs.
- Update `PROJECT_STATUS.md`, `docs/ai/PROJECT_STATE.md`, `docs/ai/NEXT_SPRINT.md`,
  `AGENTS.md`.
- Make `KAIRO_V2_ROADMAP` the canonical active execution source.
- Avoid keeping contradictory sprint status in five files.

**Acceptance**

- One obvious source of truth exists for active roadmap status.
- Historical sprints remain accessible.
- Agents can determine the next sprint deterministically.
- No stale “Sprint 98” status is treated as current after migration.

---

## Sprint 103 — Design System 2.0

Phase: STANDARDIZE. Dependencies: 102.

**Goal:** Unify visual foundations across Vue and Flutter without replacing either
framework, preserving the calm, neutral, Swiss-inspired visual language.

**Tasks**

- Formalize tokens: spacing, radii, typography, semantic colors, status semantics,
  motion, touch targets, breakpoints.
- Produce `design/tokens.json`, `design/semantics.md`, `design/components.md`.
- Map tokens to Vue/SCSS and Flutter Material 3.
- Standardize LoadingState, EmptyState, ErrorState, SuccessState, StatusBadge,
  MetricCard, PageHeader, SectionHeader, confirmation, destructive-action and
  form-validation patterns.
- Do not introduce a heavy UI framework.

**Acceptance**

- Vue and Flutter use the same semantic design language.
- WCAG touch targets remain respected.
- Dark mode remains correct in Flutter.
- Vue mobile responsiveness does not regress.
- Visual regression tests cover representative screens.

---

## Sprint 104 — Navigation And Information Architecture

Phase: SIMPLIFY. Dependencies: 103.

**Goal:** Make Kairo easier to navigate as the module count grows.

**Tasks**

- Primary mobile navigation around frequent tasks: Home, Tasks, Search,
  Notifications, More (office roles).
- Move Profile and Security into the account surface.
- Create a real `/more` destination; never secretly point to the first workspace.
- Group secondary destinations by domain: Management, Governance, Community,
  Account.
- Improve dense horizontal role navigation.
- Do not reintroduce a drawer/sidebar-heavy mobile architecture; desktop may use
  wider navigation.

**Acceptance**

- Every role can reach all authorized surfaces.
- Unauthorized surfaces remain inaccessible.
- Bottom navigation contains high-value destinations.
- More is a real navigation catalog.
- 320px mobile width has no destructive overflow.
- Keyboard navigation works.

---

## Sprint 105 — Role-Aware Action Center

Phase: EXTEND. Dependencies: 104.

**Goal:** Turn the Dashboard into an operational command center that answers
“What needs my attention now?”.

**Tasks**

- Backend-backed task/attention aggregation layer.
- Treasurer: pending receipts, overdue cash handovers, balances needing attention,
  failed finance notifications.
- Secretary: documents to process, announcements pending, policies needing
  attention, upcoming governance dates.
- President: cross-module risks, open governance actions, finance warnings,
  discipline attention.
- Member: remaining balance, new announcement, next event, new document or
  notification.
- Counts must be backend-authorized; never expose data merely to show a count.
- Priority semantics: urgent, attention, normal, informational.

**Acceptance**

- Dashboard answers what needs attention now.
- Every card has an actionable destination where appropriate.
- No cross-role data leakage.
- Desktop and mobile layouts validated.
- Empty states are meaningful.

---

## Sprint 106 — Global Permission-Aware Search

Phase: EXTEND. Dependencies: 105.

**Goal:** Find authorized information without navigating every module.

**Tasks**

- Global search with Ctrl+K / Cmd+K.
- Domains: members, documents, events, announcements, payments, receipts, audit
  entries, disciplinary records.
- Modular search providers; every provider enforces permission and tenant filtering
  BEFORE returning results.
- Never load unauthorized results and hide them in the client.
- Ranked results with type/category labels.

**Acceptance**

- Cross-module search works.
- Tenant isolation tests exist.
- Role permission tests exist.
- Search does not leak inaccessible record titles.
- Mobile search UX works; keyboard command works on Web.

---

## Sprint 107 — Web Feature Decomposition

Phase: DECOUPLE. Dependencies: 106.

**Goal:** Break oversized Vue views into maintainable feature modules without
behavior change.

**Tasks**

- Primary targets: `FinanceWorkspaceView.vue`, `DashboardView.vue`,
  `AdminMembersView.vue`, large admin views.
- Move toward `features/finance/receipts`, `custody`, `expenses`, `budget`,
  `member-balance`, `reporting`.
- Extract components, composables, API gateways, formatters, validators.
- Container views orchestrate instead of owning all business UI logic.
- No artificial micro-components for every few lines.

**Acceptance**

- Primary mega-views materially shrink.
- Business behavior unchanged; tests remain green.
- Component boundaries correspond to real domain concepts.
- No authorization logic moves into the frontend.

---

## Sprint 108 — Internationalization Refactor

Phase: SIMPLIFY. Dependencies: 107.

**Goal:** Make FR/EN/DE maintainable and consistent.

**Tasks**

- Replace the monolithic catalog with feature-scoped catalogs
  (`i18n/fr/common`, `finance`, `membership`, `governance`, … and EN/DE
  equivalents).
- Eliminate repeated `currentLocale === "fr" ? ... : ...` patterns.
- Localize user-visible enum values through mapping keys.
- CI verification that FR keys == EN keys == DE keys.
- Detect hardcoded user-facing strings.
- Do not translate backend enum identifiers themselves.

**Acceptance**

- No known mixed-language French screen remains.
- Key parity is automatic.
- Existing language selection persists.
- Web localization Playwright matrix passes.

---

## Sprint 109 — Capability-Driven Client UI

Phase: STANDARDIZE. Dependencies: 108.

**Goal:** Reduce frontend dependence on hardcoded role-name lists.

**Tasks**

- Expose authoritative effective capabilities through existing auth/tenant
  contracts.
- Refactor navigation and action visibility to consume capabilities.
- Roles remain named bundles; the frontend never becomes the authorization
  authority.
- Capability concepts: `membership.read`, `membership.manage`, `finance.read`,
  `finance.receipts.declare`, `finance.receipts.validate`,
  `finance.expenses.write`, `discipline.read`, `discipline.manage`,
  `governance.documents.write`, `audit.read`.
- Preserve canonical roles; prepare tenant-specific role bundles.

**Acceptance**

- Major navigation no longer contains large repeated arrays of role names.
- Backend enforcement remains unchanged or stronger.
- All existing roles behave correctly; role security tests pass.

---

## Sprint 110 — Finance Bounded Context Split

Phase: DECOUPLE. Dependencies: 109.

**Goal:** Refactor the oversized contribution/finance service into clear internal
domains while preserving public API compatibility.

**Tasks**

- Target structure: `finance/`, `contributions/`, `receipts/`, `custody/`,
  `expenses/`, `budgeting/`, `reminders/`, `reporting/`.
- Separate report generation from transactional finance logic.
- Separate notification triggering through contracts/events.
- Do not change finance semantics casually.
- Regression proof for: contribution creation, payment recording, receipt
  declaration, treasurer validation/rejection, cash custody handover, treasury
  confirmation, expense recording, annual budget, member statement, exports.

**Acceptance**

- Large finance service is materially decomposed.
- Transactional boundaries are explicit.
- Regression suite covers every critical workflow.
- No finance data leakage.
- Existing API clients remain functional.

---

## Sprint 111 — Identity And Notification Core Decomposition

Phase: DECOUPLE. Dependencies: 110.

**Goal:** Break oversized identity and notification services into coherent
subdomains before notification convergence.

**Tasks**

- Identity: authentication, passwords, sessions, MFA, invitations, recovery,
  tenant-user administration.
- Notifications: inbox, preferences, devices, subscriptions, outbox, delivery,
  provider adapters, operator dispatch/reconciliation.
- Preserve API contracts unless migration is explicitly tested.

**Acceptance**

- Identity service materially smaller; notification responsibilities separated.
- No MFA/session/security regression.
- Web Push and Android FCM registration preserved.
- Existing inbox remains compatible.

---

## Sprint 112 — AI Chat Domain Adapter Registry

Phase: DECOUPLE. Dependencies: 111.

**Goal:** Remove ChatService as a direct coupling hub to business modules.

**Tasks**

- Domain context provider contracts: Finance, Membership, Governance,
  Disciplinary, Events, Documents.
- Context provider registry; assistant asks authorized providers for structured
  context.
- The LLM never decides which provider may return data; authorization happens
  before context assembly.
- Do not leak unauthorized retrieved chunks; preserve RAG safety controls.

**Acceptance**

- Chat no longer imports broad internal implementations from many domains.
- Context provider tests exist.
- Existing assistant scenarios remain functional.
- Tenant and role isolation tests pass.
- Prompt-injection protections remain green.

---

## Sprint 113 — Internal Domain Events And Transactional Outbox

Phase: DECOUPLE. Dependencies: 112.

**Goal:** Decouple business modules from secondary effects through lightweight
internal domain events and a PostgreSQL-backed outbox. No Kafka, no microservices.

**Tasks**

- Domain events (for example `ReceiptValidated` → audit projection, notification
  handler, custody workflow).
- PostgreSQL-backed outbox semantics for reliability.
- Reuse or generalize the existing notification transactional outbox.
- Event fields: event ID, tenant ID, event type, aggregate/entity, occurred_at,
  correlation ID, deduplication/idempotency key, safe payload.

**Acceptance**

- Representative workflows emit domain events.
- Audit/notifications consume events without transport imports in business modules.
- Outbox is idempotent; retries are safe.
- No duplicate financial mutation after retry.

---

## Sprint 114 — Unified Notification Convergence (HIGH PRIORITY)

Phase: STANDARDIZE. Dependencies: 113.

**Goal:** Harmonize every existing notification mechanism into one coherent
platform while preserving the strongest parts of the existing implementation.
This is not greenfield work.

**Existing foundations to preserve:** authenticated tenant-scoped inbox,
`NotificationDevice`, `NotificationDeviceProfile`, `WebPushSubscription`,
`FirebasePushSubscription`, `NotificationOutboxEvent`, VAPID Web Push, Android FCM
registration, Firebase Admin backend delivery, Flutter FCM token refresh, Flutter
permission flow, background Android delivery, deep links, Celery outbox worker,
preferences and finance/discipline/announcement/event categories.

**Firebase context:** a Firebase project already exists; FCM API V1 is enabled; an
Android Firebase application exists for `org.combissportverein.kairo`. Never
hardcode sender IDs, API credentials or service-account keys. Never commit
`google-services.json` if intentionally private, Firebase Admin service account
JSON, private VAPID key or FCM credentials. Admin credentials remain server/worker
only.

**Architecture target**

```
Business operation
      |
      v
Domain Event
      |
      v
Notification Policy / Recipient Resolver
      |
      v
Transactional Notification Outbox
      |
      +------------------------+
      |                        |
      v                        v
Authenticated Inbox      Delivery Dispatcher
                               |
               +---------------+---------------+
               |                               |
               v                               v
        Web Push VAPID                   Android FCM
               |                               |
               v                               v
           Browser                       Firebase V1
               |                               |
               +---------------+---------------+
                               |
                               v
                   authenticated deep link
```

The authenticated inbox is the source of detailed notification information; push
transports are delivery hints.

**Sensitive push content policy:** never expose finance or disciplinary details on
an unauthenticated lock screen. Default push body is generic, for example:

```
Kairo
Une nouvelle notification est disponible.
```

The push may contain a safe internal target/deep-link identifier only. Detailed
content is loaded from the authenticated Kairo inbox.

**Canonical notification envelope:** `notification_id`, `event_id`, `tenant_id`,
`recipient_user_id`, `category`, `priority`, `event_type`, `target_path`,
`created_at`, `deduplication_key`, `correlation_id`, `metadata`, `push_policy`.

**Recipient resolution:** audit existing event generation before defining policies.
Do not invent broader recipients than current permissions allow. Document a
notification-event matrix (producer, event, category, eligible recipients, inbox,
Web Push, Android FCM, deep link, privacy level) covering at minimum: payment
recorded; contribution/receipt declared; receipt validated; receipt rejected; cash
handover required; cash handover completed; treasury receipt confirmed; expense
recorded; disciplinary status update; announcement published; event published;
important account/security events.

**Preferences:** one canonical contract consumed by BOTH clients; preserve
backward-compatible categories (finance, discipline, announcements, events);
preferences are server-owned so Web changes affect Android eligibility and vice
versa within the intended account/profile scope. Define whether preferences are
user-wide, tenant-user-wide or device-profile-specific, and prefer the safest model
already represented by `NotificationDeviceProfile`.

**Devices:** stable random installation ID, never account identity; every
subscription tenant/user scoped; one physical device may serve multiple Kairo
accounts without cross-account push leakage.

**Token rotation:** FCM refresh updates registration safely, avoids duplicate
active records, preserves tenant/user binding and disables obsolete tokens.

**Logout/session revocation:** logout stops authenticated notification handling for
that user context. Choose one clear model (revoke profile binding vs revoke token)
and test it.

**Invalid tokens:** permanently invalid/unregistered tokens are disabled; transient
errors use bounded retry with backoff.

**Web Push:** keep standards-based Web Push + VAPID. Do not migrate the working
browser Push implementation to Firebase merely for uniformity. The domain must be
transport-neutral.

**Service worker:** verify push reception, notification display, notification
click, deep-link routing, expired subscription handling, unread count refresh.

**Android states:** foreground, background, terminated/cold-start where reasonably
testable. Taps route through authenticated navigation and never bypass
authorization.

**Deep links:** restricted to safe internal Kairo destinations; never blindly
navigate to arbitrary external URLs from notification payloads; route guards and
backend permissions still apply.

**Outbox:** one business transaction creates its intended notification atomically.
Delivery failure never rolls back a committed business transaction. Statuses:
pending, processing, delivered (where determinable), failed, dead/terminal.
Maintain attempts and last error. Prevent duplicate processing.

**Observability:** metrics `notification_outbox_pending`,
`notification_outbox_failed`, `notification_outbox_oldest_age`,
`web_push_success`, `web_push_failure`, `fcm_success`, `fcm_failure`,
`disabled_web_subscriptions`, `disabled_fcm_tokens`. Never log notification
contents.

**Operator health UI:** show Web Push configured?, Firebase configured?, worker
running?, pending outbox count, failed deliveries, invalid subscriptions, last
successful dispatch. Never show private keys or tokens.

**Testing:** fake Web Push and fake FCM providers; CI must not require a real
Firebase service account. Cover tenant isolation, device-profile isolation,
deduplication, preference filtering, both dispatchers, invalid token disabling,
transient retry, deep-link validation, logout/session behavior, outbox retries,
multiple accounts on one device, one account on multiple devices and the sensitive
push content policy.

**Live Firebase smoke test:** explicit opt-in only (`npm run
notifications:firebase:doctor` or equivalent backend command); never automatic in
generic CI; reports only non-secret diagnostics.

**Documentation:** operator guide for Firebase project configuration, FCM API V1,
Android package identity, Admin service account placement, Docker/worker secret
mounts, environment configuration, token troubleshooting and physical-device
validation.

**Acceptance**

- One canonical notification pipeline exists.
- Detailed notification data remains authenticated.
- Web Push and Android FCM both work through the same inbox/outbox model.
- Preferences are consistent across clients; tenant isolation is tested.
- FCM token refresh is tested; expired/invalid subscriptions are disabled.
- Deep links are safe; worker retries are bounded.
- No Firebase Admin secret exists in source control.
- Vue and Flutter notification UIs work.
- Fake-provider CI tests pass; the optional real Firebase smoke test is documented.
- Notification health is observable.

---

## Sprint 115 — OpenAPI Contract And Client Parity

Phase: STANDARDIZE. Dependencies: 114.

**Goal:** Make FastAPI's contract the formal boundary shared by Vue and Flutter.

**Tasks**

- Generate/version the OpenAPI schema.
- Detect breaking API changes.
- Generate or validate typed client contracts for TypeScript and Dart. Generated
  contract types may coexist with thin hand-written gateways.
- Create a feature parity matrix.
- Cover Sprint 114 notification contracts.

**Acceptance**

- CI can detect accidental breaking contract changes.
- Vue and Flutter contract drift is reduced.
- Notification contracts are covered.
- Existing apps build.

---

## Sprint 116 — Observability And Performance

Phase: HARDEN. Dependencies: 115.

**Goal:** Make Kairo operationally diagnosable.

**Tasks**

- Formalize structured logging, request/correlation IDs, Celery task correlation,
  error classifications, Prometheus metrics, health/readiness checks, queue/outbox
  lag, backup health, notification health, AI runtime health.
- Create performance baselines at roughly 200 members, 1000 members and larger
  historical finance/audit datasets where practical.
- Measure API p50/p95, critical DB query counts, search latency, finance overview
  latency, dashboard latency, notification outbox latency.
- Fix obvious N+1 issues.

**Acceptance**

- Operator can determine why Kairo is unhealthy.
- No sensitive data appears in metrics.
- Performance regressions are measurable.
- Representative workloads remain responsive.

---

## Sprint 117 — Extensible Role And Module Framework

Phase: EXTEND. Dependencies: 116.

**Goal:** Make future Kairo modules cheap to integrate.

**Tasks**

- Module Registry abstraction; descriptor exposes module key, capabilities,
  dependencies, navigation metadata, health checks, search provider, optional AI
  context provider, domain events, feature flags.
- No arbitrary untrusted runtime plugin execution; this is an internal product
  extension framework.
- Prepare tenant-specific role bundles; preserve canonical roles.
- Demonstrate extensibility with a small non-critical sample or test module rather
  than another large business feature.

**Acceptance**

- Adding a module no longer requires edits across many unrelated central files.
- Navigation integrates through registry metadata.
- Capabilities integrate predictably.
- Search/AI provider hooks are optional.
- Dependency conflicts are detected.
- Tests demonstrate registration.

---

## Sprint 118 — Product Hardening And Release Candidate

Phase: HARDEN. Dependencies: 117.

**Goal:** Produce a trustworthy Kairo V2 release candidate.

**Tasks**

- Full regression matrix: API, Vue PWA, Flutter Web, Flutter Android,
  notifications, multi-tenancy, capabilities, finance, discipline, audit, backup,
  restore, AI optionality.
- Accessibility audit targeting WCAG 2.2 AA where practical: 320px mobile, modern
  Android viewport, desktop, keyboard navigation, reduced motion, Flutter text
  scaling, dark mode.
- Non-destructive restore drill.
- Verify production migrations from the current deployed schema; verify backup
  before migration.
- Validate notification recovery when Firebase, Web Push or Celery are temporarily
  unavailable; the business operation must remain consistent.
- Produce release notes and a deployment/rollback runbook.

**Acceptance**

- All automated gates green.
- No unresolved P0/P1 issue.
- Restore drill passes; upgrade path passes; rollback procedure documented.
- Notification convergence production-ready.
- Repository contains no production secrets.
- Release candidate can be demonstrated end-to-end.

---

## Sprint 119 — PWA-First Product Consolidation

Phase: CONSOLIDATE. Dependencies: none.

**Goal:** Make the Vue 3 PWA the canonical supported Kairo client and freeze Flutter
as legacy/reference code without deleting it.

**Tasks**

- Classify Flutter as `FROZEN / LEGACY REFERENCE` in architecture documentation,
  project status and roadmap ownership.
- Stop new Flutter business feature development while preserving the source tree.
- Remove Flutter from the default blocking CI release pipeline; retain
  optional/manual checks where useful.
- Inventory Flutter-only useful capabilities and build an explicit Flutter → PWA
  parity matrix.
- Identify notification/deep-link gaps that S120–S124 must close.
- Eliminate obsolete active-roadmap dependencies on Flutter.
- Do not delete the Flutter application.

**Acceptance**

- Vue/PWA is documented as the canonical client.
- A Flutter failure cannot make the normal `main` release pipeline red.
- Every important Flutter-only capability is available in the PWA, planned in
  S120–S124, or explicitly deprecated.
- Flutter source remains present as legacy reference.

**Artifacts:** `docs/architecture/decisions/0014-pwa-first-flutter-frozen.md`,
`docs/pwa/FLUTTER_TO_PWA_PARITY.md` (capability inventory, deprecations and the
S120–S124 notification/deep-link gap register).

---

## Sprint 120 — Unified PWA Service Worker

Phase: PWA. Dependencies: 119.

**Goal:** Create a single reliable PWA/notification Service Worker architecture with
one canonical worker and no competing registrations.

**Tasks**

- Adopt Vue 3 + Vite + `vite-plugin-pwa` with `injectManifest` and a custom Service
  Worker.
- Handle install, activate, cache lifecycle, offline strategy and update detection in
  the canonical worker.
- Handle Firebase background messaging, notification click, focused-window reuse and
  opening a new application window.
- Support `clients.matchAll()`, `client.focus()`, `clients.openWindow()` and
  `postMessage()`.
- Implement the `SERVICE WORKER → NAVIGATE(targetPath) → VUE ROUTER` contract.
- Cover app open, backgrounded, closed, multiple tabs, standalone PWA and browser
  window.

**Acceptance**

- On an Android-compatible browser, a notification click focuses the existing PWA or
  opens it.
- The PWA lands on the exact target route with no unnecessary dashboard redirect.
- Only one Service Worker controls the application origin and scope.
- Offline and update behavior remain correct.

---

## Sprint 121 — Web Push / FCM Installation Registration

Phase: PWA. Dependencies: 120.

**Goal:** Reach browser notification delivery parity with the useful Flutter
implementation through a normalized installation model.

**Tasks**

- Create or normalize the browser installation model: `tenant_id`, `user_id`,
  `installation_id`, provider, push token/subscription, platform, browser, device
  metadata, status, `created_at`, `updated_at`, `last_seen_at`, `revoked_at`.
- Implement notification permission UX, Firebase Web Messaging, VAPID configuration,
  token registration and token renewal.
- Support installation identity, multiple devices, multiple browsers, logout
  revocation, invalid-token cleanup, tenant switching and notification preferences.
- Add retry telemetry.
- Never use Firebase topics as the authorization mechanism; backend recipient
  resolution stays authoritative.

**Acceptance**

- One user can safely use multiple installations.
- No notification can leak between tenants.
- Sign-out invalidates the corresponding push binding.
- Tenant isolation tests cover installations and push tokens.

---

## Sprint 122 — Actionable Notifications And Secure Deep Links

Phase: PWA. Dependencies: 121.

**Goal:** Make notification interaction and deep links equivalent to the useful
Flutter behavior, with privacy-safe payloads and allowlisted internal routes.

**Tasks**

- Define one canonical notification envelope: `notification_id`, `event_id`,
  `tenant_id`, `event_type`, `category`, `priority`, `target_path`,
  `deduplication_key`, `correlation_id`, `safe_metadata`.
- Keep push payloads privacy-safe; sensitive detail remains behind authenticated API
  access.
- Implement push → click → application → authentication → tenant verification →
  capability verification → resource authorization → exact target.
- Never allow arbitrary external navigation from an untrusted payload; use internal
  route allowlisting or route validation.
- Fall back to the authenticated notification inbox when the target is inaccessible.
- Validate payment, contribution, receipt declaration, cash handover, treasury
  confirmation, expense, announcement, event, disciplinary and administrative cases.

**Acceptance**

- No sensitive finance or disciplinary detail appears in a push payload.
- Every notification target resolves through an allowlisted internal route.
- An inaccessible target falls back safely to the authenticated inbox.
- Representative business cases are covered by tests.

---

## Sprint 123 — White-Label Tenant Branding

Phase: WHITELABEL. Dependencies: 119.

**Goal:** Separate platform identity from tenant identity through canonical
`TenantBranding` configuration with safe Kairo defaults.

**Tasks**

- Introduce canonical `TenantBranding`: `display_name`, `short_name`, `legal_name`,
  logo, dark logo, favicon, 192/512 icons, maskable icon, primary/secondary/background/
  theme colors, notification name, support name/e-mail, custom domain.
- Apply branding consistently to authentication, navigation shell, dashboard,
  loading/splash, favicon, page title, PWA metadata, launcher identity, icons,
  notification sender and transactional email presentation where relevant.
- Provide safe Kairo defaults; no business logic may depend on branding.
- Configure the COMBIS pilot through configuration only, with no COMBIS-specific
  conditional code.

**Acceptance**

- Branding is tenant-scoped configuration, never hardcoded product logic.
- Default Kairo branding applies when a tenant has no branding.
- All listed surfaces consume the same branding contract.
- COMBIS branding requires configuration only.

---

## Sprint 124 — Tenant-Aware PWA Installation

Phase: WHITELABEL. Dependencies: 123, 120.

**Goal:** Make an installed PWA look like the tenant's own application on Android,
including tenant-aware manifest, icons, name and install UX.

**Tasks**

- Implement tenant-aware manifest, application name, short name, icon, maskable icon,
  theme color, background color, start URL and scope strategy.
- Add installation UX: `beforeinstallprompt` where available, custom CTA,
  `appinstalled`, standalone-mode detection, already-installed UX where feasible,
  browser-specific fallback guidance and post-install onboarding.
- Do not request notification permission immediately on first visit; ask after
  meaningful interaction or during an explicit notification-enablement step.
- Validate the target journey: link → authenticate/onboard → Installer `<TENANT>` →
  installation → launcher search → standalone launch.

**Acceptance**

- An installed COMBIS PWA shows `COMBIS` rather than `Kairo`.
- Manifest, icons and theme are tenant-aware and validated at phone width.
- Installation is offered without aggressive permission prompts.
- No separate frontend codebase is created per association.

---

## Sprint 125 — Tenant Domains And Host-Based Resolution

Phase: WHITELABEL. Dependencies: 123.

**Goal:** Allow association-specific addresses without duplicating deployments
through canonical host-based tenant resolution.

**Tasks**

- Support `combis.<platform-domain>`, `association-x.<platform-domain>` and prepare
  `app.customer-domain.de`.
- Implement explicit allowed-host mapping and reject unknown mappings.
- Never trust a client-supplied tenant override; enforce a canonical tenant/domain
  relation.
- Review HTTPS production requirements, cookies/session behavior, CORS, CSRF, Service
  Worker origin/scope and Web Push origin constraints.
- Document tenant onboarding: create tenant → branding → domain → TLS → principal
  admin → permissions → PWA installation.

**Acceptance**

- Host-based tenant resolution is explicit and server-authoritative.
- Unknown hosts cannot select a tenant.
- Cross-tenant leakage through domains, cookies or Service Worker scope is tested and
  prevented.
- Tenant onboarding is documented end to end.

---

## Sprint 126 — Notification Outbox Reliability

Phase: RELIABILITY. Dependencies: none.

**Goal:** Remove the production reliability gap where a processing event can be
permanently stranded after a worker crash.

**Tasks**

- Implement processing lease, processing timestamp, stale-processing detection and
  automatic reclaim.
- Add retry count, bounded retry policy, backoff, idempotent delivery, deduplication
  and failed/dead-letter state.
- Persist reason/error details and add a reconciliation task with health/metrics
  visibility.
- Apply equivalent reliability principles to domain-event dispatch where relevant.

**Acceptance**

- A simulated worker crash after claiming an event does not strand it permanently.
- Another worker reclaims the expired lease and delivers the event.
- No duplicate business side effects are produced.
- Health and metrics expose stranded, retrying and dead-letter events.

---

## Sprint 127 — Green CI, Reproducible Builds And Repository Hygiene

Phase: HARDEN. Dependencies: none.

**Goal:** Make `main` consistently green and reproducible, and remove runtime evidence
from the tracked repository without weakening security checks.

**Tasks**

- Install Tesseract correctly in CI so OCR tests pass and are never skipped.
- Ensure OpenAPI generation emits pure machine-readable JSON with no logging pollution.
- Restore generated TypeScript contract checks after the Flutter freeze.
- Remove inappropriate tracked runtime evidence without weakening the sensitive-file
  checker; move screenshots, XML dumps, Playwright artifacts, test videos, device
  captures and temporary exports to CI artifacts or non-versioned storage.
- Run secret scanning after guard checks.
- Implement Python lock/constraints, deterministic npm lock, reproducible production
  dependencies and appropriate image/version pinning.
- Build the actual production image in CI, start it and run a basic health/readiness
  check.

**Acceptance**

- Mandatory default pipeline passes: Security, API, Contracts, Web, Production.
- Flutter is not a blocking release job.
- OCR tests run and pass in CI.
- Dependency resolution is deterministic and the production image is health-checked.

---

## Sprint 128 — Real Full-Stack Release Gate And COMBIS Pilot

Phase: RELEASE. Dependencies: 122, 124, 125, 126, 127.

**Goal:** Verify Kairo as a real integrated SaaS platform with a deterministic
production-like environment and prepare the COMBIS real-device pilot checklist.

**Tasks**

- Build a deterministic production-like test environment: PostgreSQL, Redis, MinIO,
  API, Celery worker, Vue/PWA, using seeded test tenants (COMBIS roles and a Tenant X
  isolation control).
- Execute at least one important business scenario through browser → Vue → real API →
  real database → domain event → outbox → worker → notification inbox → deep-link
  contract → target route → authorization, without API mocking.
- Verify tenant isolation, role/capability authorization, finance lifecycle,
  notification creation, preferences, installation registration, logout/revocation,
  branding, tenant manifest, custom host resolution, Service Worker, PWA
  installability, application update, offline behavior where supported,
  accessibility, FR/EN/DE and responsive Android viewport.
- Prepare the explicit COMBIS real-device pilot checklist for Chrome Android,
  including closed-application notification, exact deep link, token revocation and
  application update.
- Update CURRENT_ARCHITECTURE, PROJECT_STATUS, active roadmap, notification
  architecture, PWA architecture, white-label architecture, tenant onboarding,
  deployment, COMBIS pilot instructions, known limitations and the operational
  checklist.
- Never claim production readiness unless the defined automated gates pass; pause the
  runner for manual real-device validation when no automated equivalent exists.

**Acceptance**

- The full-stack scenario passes against real seeded infrastructure without API
  mocking.
- Tenant isolation and authorization are proven for the representative scenario.
- The COMBIS pilot checklist exists and its manual steps are marked as
  human-validated or explicitly pending.
- Documentation reflects the implemented reality; no fabricated PASS is recorded.

---

## Flutter Exit Condition

Flutter is not deleted during S119–S128. After S128, archival can be considered only
when PWA installability, background/closed push, deep-link parity and the COMBIS pilot
are validated and no required Flutter-only workflow remains. Any removal is a separate
explicit change outside this roadmap.
