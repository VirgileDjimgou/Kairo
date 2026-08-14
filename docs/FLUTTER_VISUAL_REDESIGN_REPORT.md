# Flutter Visual Redesign Report

## Phase 1 — Design Foundation

**Status:** In progress  
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

### User Experience Direction

The new direction uses calm blue governance surfaces, semantic financial colours,
larger information hierarchy and softer elevation. The dashboard now foregrounds
role-aware summaries and key actions without changing the permissions or data shown
by the API. The system follows the device theme automatically, with a true dark
scheme rather than an inverted light palette.

### Migration Queue

The shared system is now available to every feature. The next phases apply it to the
high-density workspaces while preserving existing contracts:

1. members and member-detail presentation;
2. finance, receipts, contributions and treasury custody;
3. discipline, governance, audit and operations journal;
4. events, announcements, chat, notifications and offline states;
5. role-by-role phone, tablet and desktop visual evidence plus accessibility review.

### Verification Evidence

- `flutter analyze --no-pub` — passed;
- focused design-system widget test — passed;
- existing golden references were regenerated through Flutter's normal
  `--update-goldens` workflow because the rendered Material theme intentionally
  changed.

The redesign remains a progressive migration. A feature is marked visually complete
only after its responsive and accessibility evidence is captured for the roles that
may access it.
