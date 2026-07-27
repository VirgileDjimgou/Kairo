# Responsive Repair Audit

**Date**: 2026-07-27
**Auditor**: Lead Frontend Engineer (agentic)
**Scope**: All `.vue` and `.scss` files in `apps/web/src`

---

## Summary

The audit found that the codebase has a strong responsive baseline (global `min-width: 0`
reset on flex/grid children, no internal `100vw` usage, and responsive data-card support).
The primary defect sources were:

1. **Non-responsive action headers** in 4 admin views — `d-flex justify-content-between`
   without `flex-column flex-md-row` fallback, causing button groups + titles to exceed
   viewport width on 320–430px screens.
2. **Legacy alternate navigation components and tests** — the shared shell had already
   moved to the horizontal role navigation and fixed bottom navigation, but inactive
   sidebar components and assertions still described the old model.
3. **A stale 76px mobile header offset** — the module navigation was positioned below a
   header height that no longer existed after the compact top-bar refactor.

All defects have been corrected at their source.

---

## Defect Register

| # | Component | Cause | Viewport | Fix | Regression Risk |
|---|---|---|---|---|---|
| D1 | `AdminMembersView.vue` | Action headers did not stack or wrap, so titles and three actions could exceed the available line width. | 320–430px | Header actions use the mobile column layout and wrap before the desktop breakpoint. | Low — desktop resumes the row layout. | `overflow-check.spec.ts`, mobile route checks |
| D2 | `AdminContributionsView.vue`, `AdminAnnouncementsView.vue`, `AdminEventsView.vue` | Same fixed-row action pattern, compounded by filter controls or multiple buttons. | 320–430px | Each header now uses responsive stacking/wrapping; cards retain the available width. | Low | `overflow-check.spec.ts` |
| D3 | `AdminMembersView.vue`, `AdminContributionsView.vue` | CSV error tables lacked a bounded responsive wrapper and long values did not break. | 320–430px | Tables are wrapped and error content breaks within the card. | Low | `overflow-check.spec.ts` |
| D4 | `AppShell.vue`, former `DesktopSidebar.vue`, former `MobileBottomNavigation.vue` | The active shell was unified, but inactive duplicate navigation components and stale sidebar assertions could reintroduce a divergent layout. | All | Removed the unused alternate components and sidebar-only shell props; tests now assert the shared horizontal and bottom navigation at every width. | Low — no runtime imports referenced either component. | `responsive-mobile.spec.ts`, `release-candidate.spec.ts` |
| D5 | `variables.scss`, `RoleTopNavigation.vue` | `--om-mobile-topbar-height` retained a 76px offset after the top bar became 56px, leaving an incorrect sticky position. | 320–767px | It now resolves to `--om-topbar-height`; the module tabs stick immediately below the visible header. | Low | `responsive-mobile.spec.ts` visual/navigation assertions |
| D6 | `LanguageSelector.vue` | A full locale selector has a 136px minimum width and cannot share a 320px header safely with tenant identity and account actions. | 320px if full variant used | The authenticated top bar exclusively uses the 56px compact selector. | Low | `responsive-mobile.spec.ts` header overflow check |
| D7 | `variables.scss` | Palette lacked enough contrast and hierarchy for data-dense mobile screens. | All | Tokens use a deep text color, saturated accessible primary blue, and distinct semantic colors. | Low — token-only change. | visual reference captures |

---

## Architecture Changes

### Before
- Multiple navigation component variants and sidebar-oriented test assertions.

### After
- **All sizes**: Unified TopBar + RoleTopNavigation (always visible, horizontal scroll) + centered content (max-width 1280px) + BottomNav (always visible).
- Unused `DesktopSidebar.vue` and `MobileBottomNavigation.vue` removed.
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
# 2026-07-27 mobile data-view repair

The second responsive stabilization pass replaced compressed business tables with mobile cards through `ResponsiveDataView`, removed inherited `overflow-wrap:anywhere` from normal cards, stabilized bottom navigation labels, and corrected mobile action grids. Visual evidence and the exact coverage matrix are stored in `apps/web/artifacts/responsive-proof/2026-07-27/`.
