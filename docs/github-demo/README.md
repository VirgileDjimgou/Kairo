# GitHub Demo Sessions

This folder stores reusable full-stack screenshot sessions generated from the local Kairo demo environment.

## Sessions

- `sessions/00-admin/` — login, admin overview, members, documents
- `sessions/01-member-alice/` — member dashboard, profile, AI chat answer, announcements
- `sessions/02-member-bob/` — second member walkthrough focused on profile and events
- `sessions/03-treasurer/` — treasurer dashboard, finance workspace, and account security
- `sessions/04-president/` — governance persona mapped to admin workflows
- `sessions/05-secretary/` — communication and audit persona mapped to admin workflows

Each session folder contains:

- PNG screenshots
- `SESSION.md` with the account used and the captured steps

## Regenerate

Start the stack and demo seed first, then run:

```bash
node scripts/capture-github-demo.mjs
```

If your frontend runs on a different local URL, set `KAIRO_DEMO_BASE_URL` before the command.
