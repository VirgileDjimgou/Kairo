# Accessibility Audit — Kairo V2 Release Candidate

Last updated: 2026-10-03 (Roadmap V2 Sprint 119)

Target: WCAG 2.2 AA where practical for the canonical Vue 3 PWA. Flutter
(`apps/flutter_kairo/`) is frozen as legacy/reference code (ADR-014); its
historical accessibility evidence below is retained for reference and is not
part of the blocking release pipeline.

## Automated evidence

| Surface | Command | Result |
| --- | --- | --- |
| Vue PWA (axe-core WCAG 2.2 AA tags) | `cd apps/web && npm run test:e2e:a11y` | 6 Chromium tests pass |
| Vue PWA regression packs (unchanged behaviour) | `npm run test:e2e:locale`, `npm run test:e2e:roles`, `npm run test:e2e:release-candidate` | 20 + 17 + 9 pass |
| Flutter semantics, text scaling and dark mode (historical, optional) | `apps/flutter_kairo/scripts/flutter.ps1 test` | F9 release-readiness and design-system tests passed |

The browser audit (`apps/web/e2e/accessibility.spec.ts`) covers:

- public login at desktop (1280×900) and 320×568 phone width, with no horizontal
  overflow and no detectable axe violations;
- the authenticated shell at 390×844 and 1280×900, landmark (`main`) presence and
  no horizontal overflow;
- keyboard access to the main content through a visible skip link, and visible
  focus styles on the login form (email → password traversal);
- `prefers-reduced-motion: reduce`, where no element keeps an infinite animation.

Historical Flutter coverage added in Sprint 118 (reference only; the client is
frozen per ADR-014):

- sign-in at 200% Android text scaling with no overflow, semantics preserved and a
  password-visibility target of at least 44 logical pixels;
- sign-in rendered with the dark theme, verifying `Brightness.dark` and the same
  semantic labels.

## Fixes applied in Sprint 118

1. **Skip link** — `AppShell.vue` now provides a localized "skip to main content"
   link (`layout.skipToContent` in FR/EN/DE) as the first tabbable element, with
   `main#kairo-main-content` accepting programmatic focus.
2. **Subtle-badge contrast** — 101 class pairs across 24 files moved from
   `text-{variant}` to Bootstrap 5.3 `text-{variant}-emphasis` on
   `bg-{variant}-subtle` surfaces, meeting 4.5:1 for small text.
3. **Kicker labels** — 34 files moved the recurring uppercase card kicker from
   `text-secondary` to `text-secondary-emphasis`, which passes on the application
   background (`--om-neutral-50: #F3F6FA`).
4. **Login surface** — mobile brand/subtitle text darkened to
   `var(--om-neutral-600)`, demo credential hints switched to `text-body`, and
   `.btn-outline-primary` now uses the tenant-aware `--om-primary` instead of the
   Bootstrap default blue. These changes removed the last detectable contrast
   violations on the public sign-in screen.
5. **Progress bars** — all three `role="progressbar"` widgets
   (member onboarding card, admin onboarding wizard, admin overview) now carry a
   localized `aria-label` from the existing per-view copy pattern.

## Intentional limitations

- The Vue PWA has no dark theme. Dark-mode validation existed only for the
  Flutter client, which is now frozen as legacy/reference code (ADR-014).
- Automated axe coverage detects rule violations, not every usability barrier.
  Manual screen-reader passes on physical devices remain part of the operator
  pilot checklist.
- `node scripts/check-i18n-coverage.mjs` still reports hardcoded strings in a
  shrinking set of admin views. This is a tracked, non-blocking translation gap;
  it is not an accessibility regression, and every string involved is rendered
  with sufficient contrast.
