# Next Sprint

## Status

Sprint 73 (open-source maturity track) is complete. Sprint 74 through Sprint 82
have been executed and documented as the first increments of the new planning cycle.

## What Was Done

Sprint 74 - Broader Recovery UX Rollout (Censor + Sports):

- Migrated `CensorWorkspaceView.vue` and `SportsWorkspaceView.vue` to the shared
  `useRecoveryState` composable (loading, error, isRecovering, run, retry, clearError)
- Replaced bespoke inline error blocks with the standardized recovery alert
  (title + message + recovery hint + retry button with spinner)
- Added i18n keys `censor.workspaceErrorTitle` and `sports.workspaceErrorTitle`
  across all three locales (fr/en/de)
- Added E2E recovery tests: censor (fr) and sports (de) retry-after-failure flows
- Verified: 239 backend tests pass, `npm run type-check` and `npm run build` pass,
  localization E2E (9 tests) passes

Sprint 75 - Broader Recovery UX Rollout (Auditor + Governance):

- Migrated `AuditorFinanceView.vue` to the shared recovery alert pattern for load failures
- Migrated `useGovernanceCockpit.ts` and `GovernanceCockpitView.vue` to `useRecoveryState`
- Added i18n keys `auditor.workspaceErrorTitle` and `governance.workspaceErrorTitle`
  across all three locales (fr/en/de)
- Added E2E recovery tests: auditor (fr) and governance (fr) retry-after-failure flows
- Verified: `npm run type-check`, `npm run build`, and localization E2E
  (11 tests) pass

Sprint 76 - Broader Recovery UX Rollout (Secretary Documents + Principal Admin Overview):

- Migrated the document workspace used by `/secretary/documents` to the shared recovery alert pattern
- Migrated `useAdminOverview.ts` and `AdminOverviewView.vue` to `useRecoveryState`
- Added E2E recovery tests: secretary documents (fr) and principal-admin overview (fr) retry-after-failure flows
- Verified: `npm run type-check`, `npm run build`, and localization E2E
  (13 tests) pass

Sprint 77 - Broader Recovery UX Rollout (Secretary Announcements + Tenant Operations):

- Migrated `apps/web/src/views/announcements/AdminAnnouncementsView.vue` to the shared
  `useRecoveryState` composable for list loading failures while preserving separate
  local action-error handling for create/update/delete/export mutations
- Migrated `apps/web/src/views/admin/TenantOperationsView.vue` to the shared
  recovery alert pattern for current-tenant context loading while preserving
  explicit tenant switching and separate action errors
- Added E2E recovery tests: secretary announcements (fr) and tenant operations (fr)
  retry-after-failure flows
- Verified: `npm run type-check`, `npm run build`, and localization E2E
  (15 tests) pass

Sprint 78 - Broader Recovery UX Rollout (Secretary Policies + Admin Health/Onboarding/Settings):

- Migrated `apps/web/src/views/policies/AdminPoliciesView.vue` to `useRecoveryState`
  for bootstrap loading failures while preserving separate action errors for save
  and delete flows
- Migrated `apps/web/src/views/admin/AdminHealthCenterView.vue` to the shared
  recovery alert pattern for health-context loading
- Migrated `apps/web/src/composables/useTenantOnboarding.ts` and
  `apps/web/src/views/admin/AdminOnboardingWizardView.vue` to the shared
  recovery contract and aligned the onboarding route with the localized retry flow
- Migrated `apps/web/src/views/admin/AdminSettingsView.vue` to the shared
  recovery alert pattern for initial settings loading while preserving separate
  local save errors
- Added i18n keys `policies.deletePolicy` and `policies.workspaceErrorTitle`
  across all three locales (fr/en/de)
- Added E2E recovery tests: secretary policies, admin onboarding, admin health,
  and admin settings retry-after-failure flows
- Verified: `npm run type-check`, `npm run build`, and localization E2E
  (19 tests) pass

Sprint 79 - Real Notification Channel Integrations Baseline:

- Added backend live dispatch support at `POST /api/v1/notifications/dispatch`
  with tenant-administration capability checks, audit logging, and explicit
  rejection of unknown, unconfigured, or simulation-only channels
- Kept the existing multi-channel dry-run flow for diagnostics while exposing
  SMTP-backed email as the first real operator-usable notification channel in
  this module
- Updated `apps/web/src/views/admin/AdminNotificationsView.vue` so the admin
  console is localized (fr/en/de), clearly distinguishes simulation from live
  delivery, and only offers the live action when a live-capable channel exists
- Added backend regression coverage for live email dispatch, simulation-only
  rejection, and principal-admin access in `services/api/tests/test_notifications.py`
- Added browser coverage for the French notifications console, including live
  email dispatch and simulation/live state visibility, in
  `apps/web/e2e/language-coverage.spec.ts`
- Verified: `python -m pytest services/api/tests/test_notifications.py -q`,
  `npm run type-check`, `npm run build`, and localization E2E (20 tests) pass

The recovery-UX backlog identified in the continuity docs is now complete, and
the notification module is no longer fully placeholder-only: email now has a
real SMTP-backed operator dispatch path while Telegram and WhatsApp stay
simulated.

Sprint 80 - Operational Dashboards And Observability Packaging Baseline:

- Added a versioned monitoring package under `infra/monitoring/` with:
  - a Prometheus scrape baseline for the existing API `/metrics` endpoint
  - Grafana provisioning for the datasource and dashboard folder
  - a reusable `Kairo Operator Overview` dashboard
- Added `docs/operations/observability-dashboard-package.md` to document startup,
  metric mapping, safe operational scope, and how to correlate the dashboard
  with `/health`, the admin health center, and `X-Request-ID`
- Added backend regression coverage in
  `services/api/tests/test_observability_dashboard_package.py` so the packaged
  dashboard can only reference `kairo_*` metrics that `/metrics` actually emits
- Verified: `python -m pytest services/api/tests/test_observability_dashboard_package.py services/api/tests/test_observability.py services/api/tests/test_health.py -q`
  passes (15 tests), and the packaged dashboard JSON parses successfully

Sprint 81 - Broader Real Notification Channel Integrations:

- Promoted Telegram from placeholder-only to a real live-capable notification
  provider when `TELEGRAM_BOT_TOKEN` is configured
- Kept the dry-run notifications path intact while allowing the live dispatch
  endpoint to route real delivery through SMTP-backed email or Telegram
- Updated `apps/web/src/views/admin/AdminNotificationsView.vue` so its localized
  copy now reflects multiple live-capable channels instead of implying that only
  email can be real
- Added backend regression coverage for live Telegram dispatch, principal-admin
  access, and the Telegram provider contract in
  `services/api/tests/test_notifications.py`
- Updated environment examples and product docs so the repo now describes
  notifications honestly as: live SMTP-backed email plus live Telegram, with
  WhatsApp still placeholder-only
- Verified: `python -m pytest services/api/tests/test_notifications.py -q`,
  `npm run type-check`, `npm run build`, and localization E2E (20 tests) pass

Sprint 82 - WhatsApp Delivery Gateway Baseline:

- Promoted WhatsApp from placeholder-only to a live-capable gateway-backed
  notification provider when `WHATSAPP_API_BASE_URL` and `WHATSAPP_API_TOKEN`
  are configured
- Kept the existing backend-owned live dispatch flow and provider abstraction,
  so the new channel inherits the same tenant-administration capability checks
- Updated `apps/web/src/views/admin/AdminNotificationsView.vue` so its
  localized copy now reflects SMTP, Telegram, and WhatsApp as potentially real
  operator channels when configured
- Added backend regression coverage for the WhatsApp provider contract plus live
  WhatsApp dispatch by tenant admins and principal admins in
  `services/api/tests/test_notifications.py`
- Updated environment examples and product docs so the repository now describes
  notifications honestly as: live SMTP-backed email, live Telegram, and
  gateway-backed live WhatsApp
- Verified: `python -m pytest services/api/tests/test_notifications.py -q`,
  `npm run type-check`, `npm run build`, and localization E2E (20 tests) pass

Sprint 83 - Notification Delivery Reconciliation And Audit Baseline:

- Extended the backend notification dispatch contract with `delivery_stage`,
  `reconciliation_status`, `reconciliation_supported`, and
  `provider_reference` so operators can distinguish simulation, acceptance, and
  failure states honestly
- Added `GET /api/v1/notifications/history` for tenant-admin and
  principal-admin users, backed by the existing tenant-scoped audit trail and
  filtered strictly by backend capability checks
- Split dry-run audit recording into per-channel notification events so channel
  history is reviewable without depending on local frontend state
- Updated `apps/web/src/views/admin/AdminNotificationsView.vue` so the
  notifications console now reloads audited server history, displays delivery
  stage plus reconciliation status, and surfaces provider references when
  available
- Added backend regression coverage for reconciliation metadata persistence and
  history retrieval in `services/api/tests/test_notifications.py`
- Updated the Playwright notifications scenario in
  `apps/web/e2e/language-coverage.spec.ts` to validate the French audited
  history experience after a live dispatch
- Verified: `python -m pytest services/api/tests/test_notifications.py -q`
  (17 passed), `npm run type-check`, `npm run build`, and localization E2E
  (20 tests) pass

Sprint 84 - Notification Provider Callback And Final-State Reconciliation Baseline:

- Added `POST /api/v1/notifications/reconciliation/callback`, protected by a
  shared secret header and intentionally separated from the user-authenticated
  admin routes
- Added `NOTIFICATION_RECONCILIATION_CALLBACK_TOKEN` configuration so a
  provider bridge can report final outcomes without trusting the frontend
- Enforced tenant-safe correlation by requiring `tenant_id`, `channel`, and
  `provider_reference`, then matching callbacks only to existing live dispatch
  records for the same tenant
- Reused backend module-toggle enforcement so disabled notifications modules
  still reject callback writes
- Updated `GET /api/v1/notifications/history` so callback events are merged
  back into the live dispatch history, allowing operator cards to progress from
  `pending` acceptance to `delivered` or `failed`
- Updated `apps/web/src/views/admin/AdminNotificationsView.vue` and the
  localized Playwright scenario so delivered final states now render cleanly in
  the admin notifications workspace
- Added backend regression coverage for successful callbacks and invalid
  callback-token rejection in `services/api/tests/test_notifications.py`
- Verified: `python -m pytest services/api/tests/test_notifications.py -q`
  (19 passed), `npm run type-check`, `npm run build`, and localization E2E
  (20 tests) pass

## Next Planning Cycle

Sprint 74 through Sprint 84 now cover the broader recovery-UX rollout, the
observability packaging baseline, the three currently live operator
notification channels, the acceptance-level reconciliation/audit baseline, and
the secure provider callback seam. The next agent session should execute
`Sprint 85 - Notification Reconciliation Polling And Replay-Safety Baseline`,
adding replay-safe update handling plus one backend-owned polling path for
providers that cannot push reliable callbacks.

## Continuity Rule

Future agent sessions must not invent the next step from memory. They must read
`README.md`, `AGENTS.md`, `constitution/KAIRO_CONSTITUTION.md`,
`IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`, `prompts/CODEX_AUTOPILOT.md`,
and `prompts/KAIRO_CONTINUE_UNIVERSAL.md`, then decide the next increment.
