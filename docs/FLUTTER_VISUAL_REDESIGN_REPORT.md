# Flutter Visual Redesign Report

## Visual Redesign Programme

**Status:** Completed
**Scope:** Flutter client only (`apps/flutter_kairo`). The Vue 3 PWA, FastAPI
contracts, tenant isolation, authentication and role enforcement are unchanged.

### Delivered

- a centralized Material 3 visual foundation under `lib/design_system/`;
- semantic light and dark colour schemes, including success, warning, danger and
  informational states;
- shared spacing, radius and motion tokens;
- reusable accessible primitives for cards, section headers, metric cards, status
  badges, empty/loading/error panels and operation feedback;
- redesigned authenticated shell branding, role dashboard, metric overview and
  profile surface;
- global Material component styling for navigation, inputs, buttons, chips,
  snackbars, bottom sheets and cards;
- golden visual references regenerated deliberately after the approved visual
  baseline changed.

### Completed Workspace Migration

The shared system is now applied to the authenticated experience and the principal
role workspaces:

- authentication, password recovery, profile and the responsive role shell;
- role dashboards, member directory, member profile and personal contribution view;
- treasury, receipt declarations, financial member lookup, contribution history and
  expense/budget view;
- discipline, governance, recovery centre and the human-readable operations journal;
- notification inbox, optional assistant and safe empty, loading and failure states.

Every dense workspace uses responsive stacking instead of narrow columns at phone
widths. Semantic status badges and consistent feedback surfaces distinguish neutral,
informational, pending, successful, warning and error states without encoding meaning
in colour alone.

### User Experience Direction

The new direction uses calm blue governance surfaces, semantic financial colours,
larger information hierarchy and softer elevation. The dashboard now foregrounds
role-aware summaries and key actions without changing the permissions or data shown
by the API. The system follows the device theme automatically, with a true dark
scheme rather than an inverted light palette.

### Verification Evidence

- `flutter analyze --no-pub` — passed;
- `flutter test --no-pub` — 44 tests passed;
- visual evidence spans Android-width and Web golden references under
  `apps/flutter_kairo/artifacts/sprint-f3/` through `sprint-f9/`;
- golden references were regenerated through Flutter's normal `--update-goldens`
  workflow because the rendered Material theme intentionally changed.

The redesign does not alter any API contract, role permission, tenant filter or
business rule. Release signing and production promotion remain the separate F9
operational gate.

### Roles And Screens Verified

The visual regression coverage includes the member, president, secretary general,
treasurer, auditor and censor journeys. The shared role shell is also exercised with
administrator, vice-president and sports-manager sessions through the established F8
device evidence. All roles therefore use one visual language; only backend-authorised
navigation and actions vary.

| Area | Visual evidence |
| --- | --- |
| Sign-in and secure account access | `artifacts/sprint-f9/sign-in-android.png`, `sign-in-web.png` |
| Member and contribution experience | `artifacts/sprint-f3/member-android-contributions.png` |
| Treasurer and auditor finance | `artifacts/sprint-f4/treasurer-android-budget.png`, `auditor-web-read-only.png` |
| Discipline and governance | `artifacts/sprint-f5/censor-android-discipline.png`, `president-web-read-only.png` |
| Assistant and notification centre | `artifacts/sprint-f6/android-private-assistant.png`, `web-notification-inbox.png` |
| Offline states and native permissions | `artifacts/sprint-f7/`, `artifacts/sprint-f8/` |

### Files And Dependencies

The reusable implementation lives under `lib/design_system/`; the feature changes are
limited to existing Flutter presentation files and `lib/app/kairo_app.dart`. No new UI
library was introduced: Material 3 and the project’s existing dependency set are used.
This keeps APK size, web bundle risk and maintenance surface controlled.

### Commands Executed For Final Validation

```text
flutter analyze --no-pub
flutter test --no-pub
flutter build web --release --no-pub --dart-define=KAIRO_FLAVOR=development
flutter build apk --debug --no-pub
```

All commands completed successfully. The Android build reports an upstream Flutter
future-compatibility warning for `file_picker` and `share_plus` applying the Kotlin
Gradle Plugin; it is not a build failure and should be handled during normal dependency
maintenance before Flutter makes the migration mandatory.
