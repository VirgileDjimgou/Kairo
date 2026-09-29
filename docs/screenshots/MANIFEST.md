# Kairo README Screenshot Gallery

Captured against the seeded demo tenant (local Docker core stack, current working tree)
in locale `fr` at desktop (1440×900) and phone (390×844) widths.

Each capture authenticates through the real FastAPI login contract and screenshots an
authorised role surface. No permission is simulated in the client.

Regenerate with:

```bash
node scripts/capture-readme-screenshots.mjs
```

A deployment with rotated demo passwords passes the public `VITE_DEMO_ACCOUNTS`
payload through `KAIRO_SCREENSHOT_ACCOUNTS`. Point the capture at another instance with
`KAIRO_SCREENSHOT_BASE_URL` and label it with `KAIRO_SCREENSHOT_TARGET_LABEL`.

> Capture-time note: the deployed reverse proxy currently normalises slash-less
> FastAPI collection routes with an absolute `http://` redirect, which an HTTPS browser
> blocks as mixed content. The script rewrites those requests to their canonical
> trailing-slash HTTPS form so the captured UI reflects the real, working surface.

## Captured surfaces

| Folder | File | Route |
| --- | --- | --- |
| `public` | `01-demo-landing.png` | `/demo` |
| `public` | `02-login.png` | `/login` |
| `member` | `01-dashboard.png` | `/dashboard` |
| `member` | `02-contribution-statement.png` | `/members/profile` |
| `member` | `03-events.png` | `/events` |
| `member` | `04-announcements.png` | `/announcements` |
| `member` | `05-private-assistant.png` | `/chat` |
| `president` | `01-dashboard.png` | `/dashboard` |
| `president` | `02-governance-cockpit.png` | `/governance` |
| `president` | `03-member-management.png` | `/members/manage` |
| `president` | `04-operation-journal.png` | `/operation-journal` |
| `president` | `05-recovery-center.png` | `/recovery` |
| `secretary` | `01-overview.png` | `/secretary` |
| `secretary` | `02-documents.png` | `/secretary/documents` |
| `secretary` | `03-announcements.png` | `/secretary/announcements` |
| `treasurer` | `01-dashboard.png` | `/dashboard` |
| `treasurer` | `02-finance-workspace.png` | `/finance` |
| `treasurer` | `03-receipt-declarations.png` | `/receipts` |
| `oversight` | `01-auditor-finance.png` | `/finance-audit` |
| `oversight` | `02-censor-discipline.png` | `/censor` |
| `oversight` | `03-sports-workspace.png` | `/sports` |
| `oversight` | `04-account-security.png` | `/account/security` |
| `notifications` | `01-inbox.png` | `/notifications` |
| `admin` | `01-overview.png` | `/admin` |
| `admin` | `02-health-center.png` | `/admin/health` |
| `admin` | `03-notification-console.png` | `/admin/notifications` |
| `admin` | `04-tenant-operations.png` | `/admin/tenants` |
| `admin` | `05-onboarding.png` | `/admin/onboarding` |
| `admin` | `06-settings.png` | `/admin/settings` |
| `mobile` | `01-member-dashboard.png` | `/dashboard` |
| `mobile` | `02-member-contribution-statement.png` | `/members/profile` |
| `mobile` | `03-treasurer-finance.png` | `/finance` |
| `mobile` | `04-president-governance.png` | `/governance` |
| `mobile` | `05-admin-health.png` | `/admin/health` |
