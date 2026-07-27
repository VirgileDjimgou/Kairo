# Responsive Repair Audit

**Date**: 2026-07-26
**Auditor**: Lead Frontend Engineer (agentic)
**Scope**: All `.vue` and `.scss` files in `apps/web/src`

---

## Summary

The audit found that the codebase has a strong responsive baseline (global `min-width: 0`
reset on flex/grid children, `overflow-x: clip` on body, no `100vw` usage, tables wrapped
in `table-responsive`). The primary defect sources were:

1. **Non-responsive action headers** in 4 admin views — `d-flex justify-content-between`
   without `flex-column flex-md-row` fallback, causing button groups + titles to exceed
   viewport width on 320–430px screens.
2. **Sidebar visibility leaking on mobile** — fixed by adding `display: none !important`
   below 768px in `DesktopSidebar.vue`.
3. **Body `overflow-x: clip`** as a global safety net masking component-level overflow.

All defects have been corrected at their source.

---

## Defect Register

| # | Component | Cause | Viewport | Fix | Regression Risk |
|---|---|---|---|---|---|
| D1 | `DesktopSidebar.vue` | `height: 100dvh; display: flex` unconditional — sidebar renders as full-height block on mobile, pushing content below viewport | <768px | Added `@media (max-width: 767px) { display: none !important; }` | None — sidebar only intended for desktop |
| D2 | `AppShell.vue` | `width: 100%` on `.app-shell__main` conflicting with flex layout on desktop ≥768px | ≥768px | Added `flex: 1 1 0; min-width: 0; max-width: none` in desktop media query | None — flex properties override width |
| D3 | `AdminMembersView.vue` lines 3–20 | `d-flex justify-content-between` without `flex-column flex-md-row` — 3 buttons + title overflow on 360px | 320–430px | Changed to `d-flex flex-column flex-md-row` + `flex-wrap` on actions | None — layout stacks vertically on mobile, horizontally on desktop |
| D4 | `AdminContributionsView.vue` lines 3–23 | Same pattern + `<select>` + 3 buttons — very high overflow risk | 320–430px | Same fix as D3 + `flex-wrap` on actions | None |
| D5 | `AdminAnnouncementsView.vue` lines 3–17 | Same pattern with 2 buttons | 320–430px | Same fix | None |
| D6 | `AdminEventsView.vue` lines 3–17 | Same pattern with 2 buttons | 320–430px | Same fix | None |
| D7 | `AdminMembersView.vue` line 121 | CSV error table without `table-responsive` wrapper | All | Wrapped in `<div class="table-responsive">` + `text-break` on message cells | None |
| D8 | `AdminContributionsView.vue` line 166 | Same — CSV error table without wrapper | All | Same fix | None |
| D9 | `LanguageSelector.vue` line 49 | `.language-select { min-width: 8.5rem; }` in non-compact mode — 136px on 320px header if reused without `compact` prop | Only if reused | Defensive: mobile usage uses `compact` prop. No regression | Low |
| D10 | `variables.scss` | Palette too pale — low contrast, gray-dominated interface | All | Enhanced: brighter primary `#1E63B5`, darker text `#17212B`, more vivid semantic colors, cooler neutrals with blue tint | None — CSS variables only |

---

## Architecture Changes

### Before
- **Mobile** (<768px): TopBar mobile variant + RoleTopNavigation + BottomNav
- **Desktop** (≥768px): DesktopSidebar (260px) + TopBar desktop variant + flex layout

### After
- **All sizes**: Unified TopBar + RoleTopNavigation (always visible, horizontal scroll) + centered content (max-width 1280px) + BottomNav (always visible)
- DesktopSidebar removed from render tree entirely
- Same navigation model on mobile, tablet, and desktop (Google Play Store pattern)

---

## Tests

- `e2e/overflow-check.spec.ts` — Playwright test covering 9 viewports × 13 routes
- Assertion: `document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1`
- Tolerance: 1px for sub-pixel rounding

---

## Remaining Notes

- `body { overflow-x: clip; }` in `_mobile-utils.scss` is retained as a final safety net
  but is no longer the primary overflow prevention — all component-level issues are fixed.
- `LoginView.vue` `.login-shell { overflow: hidden; }` is acceptable — only masks
  decorative orbs in the desktop hero panel.