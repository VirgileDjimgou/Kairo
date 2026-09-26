# Kairo Design Semantics

Companion to `design/tokens.json` (values) and `design/components.md` (patterns).
This file defines **meaning**: what each semantic role means and when it applies.
It is platform-neutral; the Vue and Flutter bindings implement the same meanings.

Principle: calm, neutral, Swiss-inspired — neutral surfaces, precise typography,
restrained motion. Meaning is never carried by colour alone: every status pairs a
colour with an icon or a text label.

## Status semantics

Four semantic status roles. Both platforms map their concrete palettes to these
roles; no other status colours exist.

| Role | Meaning | Paired signal | Examples |
| --- | --- | --- | --- |
| `positive` | Finished, settled, healthy | check icon / explicit label | paid, active, completed, validated |
| `attention` | Waiting or due; needs a human | clock/pause icon | pending, open, due soon, in review |
| `critical` | Overdue, failed or destructive | alert icon | overdue, suspended, rejected, failed |
| `info` | Neutral guidance, no risk | info icon | informational, in progress |

Rules:

- A badge shows the label; colour is reinforcement only.
- `critical` doubles as the destructive-action colour (delete, revoke, reject).
- Dark mode keeps the same meanings with adjusted foregrounds for contrast
  (see the `dark`/`subtleDark` values in `tokens.json`).

## Page and section hierarchy

- **PageHeader** owns the page title, one-line lead and page-level actions.
- **SectionHeader** owns a block title inside a page (uppercase kicker + title).
- Body text never exceeds 70–80 characters per line in reading surfaces.

## State semantics

| State | When | Contract |
| --- | --- | --- |
| Loading | First fetch in progress | Never a bare spinner: a labelled panel that says what is loading |
| Empty | Loaded, zero authorized items | Explains the state and offers the next action when one exists |
| Error | Load failed (network/5xx/4xx) | Title + short reason + recovery hint + Retry; no raw stack traces |
| Success | A mutation completed | Short confirmation near the trigger; survives navigation for one cycle |

Recovery copy stays privacy-safe: it never reveals whether hidden records exist.

## Confirmation and destructive actions

- Every mutation that changes money, membership standing, roles or data
  retention requires an explicit confirmation that names the object and the
  consequence.
- Destructive actions use `critical` colour, require the confirmation, and are
  never the default focus of a dialog.
- Cancel is always available and is the safe default.

## Form validation

- Invalid fields are marked in place with a field-specific message and a summary
  warning at the top of the form.
- Validation messages are localized (FR/EN/DE) and state how to fix the input.
- Required fields are marked before submission, not after.

## Accessibility contract

- Touch targets: ≥ 44×44 CSS px (`touchTarget` token).
- Keyboard: every action reachable, visible focus, logical order.
- Contrast: text and essential icons meet WCAG AA against their surface in both
  brightness modes.
- Text scales to 200% without clipping in phone layouts (320px band).
- Motion honours `prefers-reduced-motion` (Web) and reduces to opacity changes.

## Responsive bands

- Phone (320px+): single column, stacked full-width actions, bottom navigation.
- Tablet (768px+): 6-column grid, two-column card flows where useful.
- Desktop (1024px+): 12-column grid, wider navigation, multi-column dashboards.
- Content max width 1280px; 320px must never overflow destructively.

## Dark mode

Flutter renders full light/dark themes (`AppTheme.light/dark`) driven by the
status `dark` values in `tokens.json`. The Vue PWA currently ships the light
theme; any future dark mode must reuse these semantic values rather than
introducing a parallel palette.
