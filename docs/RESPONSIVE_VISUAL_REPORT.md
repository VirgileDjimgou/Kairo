# Responsive Visual Report

## Visual Direction

The authenticated product now uses a compact operational shell rather than separate role-specific mobile frames. The visual hierarchy is deliberately stable:

1. A tenant identity and account header stays at the top.
2. A role-derived horizontal module strip provides every permitted workspace.
3. Content owns the central scroll area.
4. A five-item bottom dock gives fast access to stable personal actions.

The palette uses a more legible blue primary (`#1e63b5`), white structural surfaces, blue-gray backgrounds, clear separators, and semantic status colors. The dock is a flat opaque bar rather than a floating dark capsule so it remains predictable against forms, tables, and long pages.

## Verified Mobile Capture

| Route        | Role                   |        Viewport | Result                                                                                                                                                                                                                                                       |
| ------------ | ---------------------- | --------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/dashboard` | Member mock            |         320x568 | Shared header, horizontally scrollable role navigation, and five-column dock visible. No legacy mobile drawer is present. Document width was 305 px and client width was 305 px after scrollbar allocation. Each dock action measured about 59.35 x 67.2 px. |
| `/dashboard` | Secretary-general mock |         390x844 | The role strip includes `/secretary` alongside permitted personal and community modules. The dock has five actions, legacy drawers are absent, and the document has no horizontal overflow.                                                                  |
| `/login`     | Guest                  | Browser capture | The email/password form remains readable and contained with no horizontal page spill.                                                                                                                                                                        |

The captured mobile dashboard shows the intended hierarchy: tenant mark and language/account actions at the top, modules in the horizontal strip, primary content in the center, and the five equal dock actions at the bottom.

## Route Matrix

| Surface             | Mobile treatment                                                      | Desktop treatment                      |
| ------------------- | --------------------------------------------------------------------- | -------------------------------------- |
| Member portal       | Shared shell, role tabs, five-action dock                             | Shared shell with sidebar              |
| Secretary workspace | Uses the member shell and secretary role tab; no nested shell         | Shared shell with role-derived sidebar |
| Admin console       | Shared shell and admin role tabs; no hamburger or drawer              | Shared shell with `.admin-sidebar`     |
| Chat                | Full-width conversation list/content overlay on phones; safe composer | Shrinkable split pane                  |
| Contributions       | Record cards below 992 px                                             | Complete data table from 992 px        |
| Finance workspace   | Record cards below 992 px                                             | Complete data table from 992 px        |

## Validation Status

- TypeScript passed after layout migration, legacy component removal, and responsive data-view conversion.
- Vite production build passed after the shell, dock, containment, and chat changes.
- Browser inspection at 320x568 confirmed no document overflow, five equal dock columns, minimum 44 px targets, and no legacy drawer nodes.
- The complete Playwright suite has been updated to use DOM-content readiness rather than `networkidle`, include all required dimensions and role scenarios, and check the shared-shell invariants. Its final terminal run must be repeated once the local terminal output channel is available; no failed assertion was reported after the dock grid repair.

## Remaining Visual Follow-up

- Capture persisted Playwright screenshots for documents, members, audit, settings, and admin overview after the final full suite run.
- Convert the remaining wide operational tables progressively, prioritizing documents, members, policies, disciplinary, and sports.
- Constrain audit detail pills as a focused next responsive maintenance slice.
