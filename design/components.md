# Kairo Component Patterns

Companion to `design/tokens.json` (values) and `design/semantics.md` (meaning).
This catalog is the standard for shared UI patterns on BOTH clients. Each entry
defines the contract; the implementation column names the code that fulfils it.

Status tone aliasing: the semantic roles (`positive`, `attention`, `critical`,
`info`, `neutral`) are implemented with platform tone names — Vue
`StatusBadge` tones `success|warning|danger|info|neutral` map 1:1 to
`positive|attention|critical|info|neutral`; Flutter `AppStatusVisual` maps
`paid/active/closed → positive`, `pending/open → attention`,
`overdue/suspended → critical`, `info → info`.

## State patterns

### LoadingState

Contract: never a bare spinner — a labelled panel that says what is loading.
- Vue: `components/ui/SkeletonLoader.vue` + the labelled `alert` loading panels
  in workspaces (spinner + heading + body copy).
- Flutter: `design_system/components/app_state_panel.dart` (loading variant).

### EmptyState

Contract: explains the zero-data state and offers the next action when one
exists. Privacy-safe copy (never reveals hidden records).
- Vue: `components/ui/EmptyState.vue` (title, description, icon, action).
- Flutter: `app_state_panel.dart` (empty variant).

### ErrorState

Contract: title + short reason + recovery hint + Retry with in-button progress.
No raw stack traces; privacy-safe recovery copy.
- Vue: `components/ui/ErrorState.vue` (shared primitive; the established
  `useRecoveryState` recovery alert matches this contract).
- Flutter: `app_state_panel.dart` (error variant) + `app_feedback.dart`.

### SuccessState

Contract: short confirmation near the trigger; one visible cycle.
- Vue: `components/ui/SuccessState.vue` + operation toasts
  (`toast.operationSucceeded`) and inline `successMessage` banners.
- Flutter: `app_feedback.dart` success feedback.

## Display patterns

### StatusBadge

Contract: label always visible; colour is reinforcement; `role="status"`.
- Vue: `components/ui/StatusBadge.vue`.
- Flutter: `design_system/components/app_status_badge.dart`.

### MetricCard

Contract: uppercase kicker label, large value, optional hint; semantic tone on
the value only.
- Vue: `components/ui/MetricCard.vue`.
- Flutter: `design_system/components/app_metric_card.dart`.

### PageHeader

Contract: page title, one-line lead, page-level actions on the right (stacked
full width on phone).
- Vue: `components/ui/PageHeader.vue`.
- Flutter: page scaffolds + `app_section_header.dart` for internal headers.

### SectionHeader

Contract: uppercase kicker, block title, optional description, optional action
slot.
- Vue: `components/ui/SectionHeader.vue`.
- Flutter: `design_system/components/app_section_header.dart`.

## Action patterns

### Confirmation

Contract: names the object and the consequence; Cancel is the safe default;
localized copy (FR/EN/DE).
- Vue: `components/ConfirmModal.vue`.
- Flutter: confirmation dialogs in feature controllers (e.g. receipt, member,
  tenant switch flows).

### Destructive action

Contract: `critical` colour, explicit confirmation, never the default focus,
never placed next to the primary constructive action without separation.
- Vue: `ConfirmModal.vue` delete variant (`.btn-danger`), guarded workspace
  actions (member delete is president/secretary only).
- Flutter: destructive actions behind confirmation dialogs in feature
  controllers.

## Form validation

Contract: required fields marked before submission; invalid fields marked in
place with a field-specific localized message plus a summary warning at the top
of the form; no submission of invalid payloads.
- Vue: shared warning banner + per-field `.is-invalid` + guidance copy
  (member creation and receipt declaration flows).
- Flutter: form validation in feature forms with localized field messages.

## Adoption status

The Vue shared primitives above are the canonical target for view refactoring.
Views that still embed equivalent markup migrate to them during the web feature
decomposition (Roadmap V2 S107), which is the designated moment to change view
structure without mixing a redesign into it. Behavior and copy must remain
identical during that migration.

## Visual regression coverage

- Flutter: 14 golden tests (`test/sprint_f*_visual_proof_test.dart`,
  `sprint_f9_release_readiness_test.dart`) cover representative screens at
  390×844 (phone) and 1280×900 (desktop) — sign-in, member statement, treasurer
  budget/custody, censor discipline, president read-only, assistant citations,
  inbox, offline status, notification inbox, document import, sync status.
  Goldens are compared on the pinned Flutter toolchain (3.44.9).
- Vue: responsive and role journeys are covered by the Playwright packs
  (locale 20, roles 17, release-candidate 9), including mobile-width checks
  (e.g. full-width export rows at 390px). Pixel-gated screenshot comparison is
  intentionally not used on the Web yet because baseline images are not
  portable across OS runners; Flutter goldens carry the pixel gate.
