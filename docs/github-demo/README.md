# GitHub Demo Assets

This folder stores reusable screenshot assets for the Kairo README, demos, and product walkthroughs.

## Full-Stack Sessions

The historical `sessions/` folder contains screenshots captured against the seeded local stack:

- `sessions/00-admin/` — login, admin overview, members, documents
- `sessions/01-member-alice/` — member dashboard, profile, AI chat answer, announcements
- `sessions/02-member-bob/` — second member walkthrough focused on profile and events
- `sessions/03-treasurer/` — treasurer dashboard, finance workspace, and account security
- `sessions/04-president/` — governance persona mapped to admin workflows
- `sessions/05-secretary/` — communication and audit persona mapped to admin workflows

Regenerate those seeded sessions with:

```bash
node scripts/capture-github-demo.mjs
```

## Role Gallery

The `role-gallery/` folder contains the current README gallery for the professional association role track:

- public entry surface
- multi-tenant picker
- member
- secretary general
- treasurer
- auditor
- censor
- sports manager
- president
- vice president
- principal admin
- tenant switcher
- secondary tenant shell

These captures are browser-driven and deterministic. They validate the live frontend routes and role matrix without requiring a Dockerized multi-tenant demo stack.

Regenerate the role gallery with:

```bash
node scripts/capture-readme-gallery.mjs
```

If your frontend is already running on a different local URL, set `KAIRO_DEMO_BASE_URL` before either command.
