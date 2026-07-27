# Visual QA report — 2026-07-27

## Outcome

PASS for the inspected responsive scope.

The screenshots were opened and checked after generation. The original compressed desktop tables are replaced by mobile cards on the finance-audit, discipline, members, access, events, announcements, contributions, and audit paths. Normal words no longer inherit `overflow-wrap:anywhere`; technical identifiers retain controlled wrapping.

Confirmed visually:

- no normal label or action rendered one character per line;
- cards remain inside 320–430 px viewports;
- finance amounts remain on one line;
- event, announcement, discipline, member, and access actions remain usable;
- UUIDs stay within audit cards;
- contribution cards lead with the member name and code;
- admin overview actions form a mobile grid;
- chat sidebar stays in the normal mobile layout flow;
- bottom navigation uses five equal items labelled Accueil, Profil, Sécurité, Chat, Plus;
- the active top-navigation item is fully visible.

The fixed bottom navigation appears in the middle of some `fullPage` screenshots because Playwright composites fixed elements at their viewport position. In the real viewport it remains fixed to the bottom; the geometry assertions validate equal-width items and 44 px touch targets.

## Technical checks

- `npm run type-check`: PASS
- `npm run build`: PASS
- Responsive proof, Chromium: 21 passed, 4 platform skips
- Responsive proof, WebKit: 4 passed, 12 platform skips
- Auditor/censor/access targeted suite: 7 passed; the remaining access cancellation scenario passed after its date-sensitive fixture was moved beyond 2026-07-27
- Public root, health, and metrics: HTTP 200
- Production entry asset: `assets/index-DA61x8BX.js`

The legacy login section of `responsive-mobile.spec.ts` still observes duplicate transition DOM under the Vite test server and can select a hidden copy. The deployed login page was separately captured in Chromium and WebKit and is visually correct. This harness issue does not affect the authenticated responsive proof suite.

