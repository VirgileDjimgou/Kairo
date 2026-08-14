# Flutter UI audit — Kairo

**Date:** 2026-08-14  
**Scope:** Flutter Android and Flutter Web companion client only. The Vue 3 PWA and
FastAPI policies are explicitly out of scope for this visual programme.

## Baseline

- Flutter `3.44.9`, Dart `3.12.2` (local SDK declared by the project status).
- Material 3 is already enabled, using Flutter's built-in Material component set.
- State is intentionally lightweight and feature-owned (`StatefulWidget`,
  `ChangeNotifier` controllers and typed gateways); no visual redesign requires a
  new state-management package.
- The application uses a single `MaterialApp` and `onGenerateRoute`; authenticated
  navigation is composed by `RoleShell` rather than by a public URL router.
- The API remains the source of truth for tenant isolation, permissions, finance,
  disciplinary decisions, recovery and identity.

## Existing visual foundations

| Area | Current state | Audit finding |
| --- | --- | --- |
| Theme | `app/theme/kairo_theme.dart` exposes a light Material 3 theme | No dark theme, no semantic status mapping, and several view-local colours/spacings remain. |
| Navigation | `RoleShell` provides adaptive rail/bottom navigation and an overflow sheet | Functional and role-aware; it needs a clearer hierarchy, an intentional `More` surface and stronger selected states. |
| Layout | `LayoutBuilder` is used in shells and major pages | Responsive intent is sound, but spacing/radii are not centralised and phone-first card composition varies. |
| Feedback | Dialogs, inline errors and some SnackBars exist | Loading, empty, error and success states need a consistent visual language. |
| Accessibility | Existing semantic password toggle regression test; Material controls used | Preserve labels, contrast and touch targets; add text-scale and dark-mode coverage during migration. |
| Localisation | French, English and German localisations are available | New reusable visual components must contain no hard-coded product copy. |

## Screen and module inventory

| Domain | Flutter surface | Roles / access is API-authorised | Main visual migration need |
| --- | --- | --- | --- |
| Access | Login, MFA, tenant selection, password replacement, account security | All authenticated users / recovery policy | Auth hierarchy, meaningful error/loading states, accessible password and session controls. |
| Shell and profile | `RoleShell`, dashboard, profile, language and overflow menu | All; destinations vary per returned roles | Reference experience for navigation, role greeting, priorities and profile. |
| Members | Searchable directory, detail, create/edit, pause/reactivate | Principal admin, president, vice president, secretary general and authorised office roles | Replace dense/table-like presentation with member cards, filters and master/detail layout. |
| Contributions | Personal statement | Member and authorised finance readers | Finance status cards and clear payment timeline. |
| Receipts / custody | Declaration, review, validation, rejection and closure | Declaring officers and treasurer | Phone-first form sections, custody timeline and controlled confirmation patterns. |
| Finance | Budget, expenses, exports and member finance search | Treasurer write; auditor read-only | Metric surfaces, semantic chart/status colours and concise mobile action hierarchy. |
| Governance | Discipline, policies, documents, events, announcements, recovery | Role-gated; censor writes discipline, president/secretary read | Professional record cards, timelines and readable lists rather than compressed data. |
| Operations journal | Human-readable audit list/detail | Authorised office roles | Expandable mobile audit cards; short copyable IDs only inside details. |
| Notifications | Inbox, preferences and deep-link entry | Authenticated API-targeted users | Category/status cards, unread priority and clear action affordances. |
| Chat | Conversations, streamed answer, citations and runtime states | API-authorised users | Messaging composition, distinct assistant states and retry feedback. |
| Offline | Banner, scoped cache/drafts and recovery feedback | Authenticated users, scoped by tenant/user | Persistent but unobtrusive connectivity/status pattern. |

## Role inventory

Canonical roles found in the API seed/catalog and consumed by the Flutter shell:

- `principal_admin`, `admin`
- `president`, `vice_president`
- `secretary_general`
- `treasurer`, `auditor`
- `censor`, `sports_manager`
- `member`

The visual system must be shared. A role changes available modules and priority data;
it must never create a separate visual product or grant local permissions.

## Existing common components and duplication hotspots

- Shared: Material `Card`, `Chip`, `NavigationBar`, `NavigationRail`, `AppBar`,
  `FilledButton`, dialogs and current `KairoTheme`/`KairoColors`.
- Repeated patterns: cards with independent padding/radius, status colour selection,
  section headings, empty/error/loading branches, confirmation dialogs and compact
  action rows.
- High-value first extraction: tokens, semantic statuses, app surface card, section
  header, metric card, state panel, status badge and action-list tile.

## Migration order

1. Create central Material 3 light/dark themes, tokens and foundational components.
2. Rebuild app shell, dashboard, profile and navigation as the visual reference.
3. Migrate member, contribution, receipt and finance surfaces.
4. Migrate governance, notifications, chat and security surfaces.
5. Verify every role at compact, medium and expanded widths; then run dark-mode,
   text-scale and visual regression checks.

## Guardrails

- No backend route, RBAC, tenant filter, cache scope or business rule is changed for
  visual work.
- No password, notification token or sensitive identifier is rendered by new shared
  components.
- All destructive operations retain their API-authorised confirmation flows.
- Flutter Web remains a separate client and never replaces the production Vue PWA
  without explicit association approval.
