<div align="center">

# Kairo

**Secure, role-aware operations for associations and community organisations.**

Membership · Treasury · Governance · Discipline · Communications · Documents · optional private AI

[**Live portfolio demo →**](https://kairo.patrickdjimgou.dev/demo) &nbsp;·&nbsp;
[Architecture](#architecture) &nbsp;·&nbsp;
[Screenshots](#screenshots) &nbsp;·&nbsp;
[Quick start](#quick-start) &nbsp;·&nbsp;
[Documentation](#documentation)

<br />

[![CI](https://github.com/VirgileDjimgou/Kairo/actions/workflows/ci.yml/badge.svg)](https://github.com/VirgileDjimgou/Kairo/actions/workflows/ci.yml)
![Vue 3](https://img.shields.io/badge/client-Vue_3-42b883?logo=vuedotjs&logoColor=white)
![Flutter](https://img.shields.io/badge/client-Flutter-02569B?logo=flutter&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/data-PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/runtime-Docker-2496ED?logo=docker&logoColor=white)
[![License: MIT](https://img.shields.io/badge/license-MIT-1f6feb.svg)](LICENSE)

</div>

![Kairo treasury workspace with annual budget, income and expense breakdowns](docs/screenshots/treasurer/02-finance-workspace.png)

---

## Why Kairo

Community organisations run on a handful of elected volunteers who each need a very
different view of the same data: the treasurer validates money, the secretary keeps
records, the president oversees, and members simply want to know where they stand.

Kairo turns that into one multilingual, multi-tenant platform where **every role sees
exactly what it is allowed to see**, sensitive decisions are enforced on the server, and
the whole thing still feels simple on a phone.

- **Server-owned authorisation** — the client never grants a permission by itself.
- **Role-focused workspaces** — no overwhelming admin console, no accidental data leaks.
- **Money you can audit** — contributions, custody handover, expenses and exports with a
  human-readable operations journal.
- **French-first, three languages** — French, English and German from the first screen.
- **Optional private AI** — a local Ollama/Qdrant assistant that stays behind the API and
  never sees an unauthorised chunk.

## Try it in one click

The public portfolio demo needs no account. Open the demo page, pick a role, and the
matching workspace opens with fictional seed data.

<p align="center">
  <a href="https://kairo.patrickdjimgou.dev/demo"><img alt="Kairo one-click role demo" src="docs/screenshots/public/01-demo-landing.png" width="820" /></a>
</p>

| Step | What happens |
| --- | --- |
| 1. Open `/demo` | Public entry point, no sign-up |
| 2. Pick a role | Member, President, Treasurer, Secretary General, Auditor, Censor or Sports Manager |
| 3. Explore | The role workspace opens with a guided three-step tour |
| 4. Switch or exit | The demo banner lets a visitor change role or leave the demo |

> The demo tenant contains fictional data only. Administrative roles are grouped under
> "advanced roles" and are aimed at a guided walkthrough.

Demo mode is configured at build time through `apps/web` variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_DEMO_MODE` | `true` | Set to `false` to hide `/demo` and the demo banner |
| `VITE_DEMO_TENANT_SLUG` | `demo` | Tenant used by one-click demo sessions |
| `VITE_DEMO_ACCOUNTS` | seed accounts | JSON array overriding the demo account catalogue |

Point `VITE_DEMO_ACCOUNTS` at the instance's real demo credentials when they differ from
the seed (for example after a password rotation), then rebuild the web image. Use the
base64 form `VITE_DEMO_ACCOUNTS_B64` when the passwords contain characters that are
awkward in an env file.

## Screenshots

Every capture below is a real screen from the running application, taken against the
public demo tenant in French at desktop and phone widths.

### Member portal — clarity for everyday members

Members get a read-first portal: their contribution statement, permitted documents,
events and announcements. Nothing more, nothing less.

<table>
  <tr>
    <td width="50%" valign="top"><strong>Personal dashboard</strong><br /><img alt="Member dashboard" src="docs/screenshots/member/01-dashboard.png" width="420" /></td>
    <td width="50%" valign="top"><strong>Contribution statement &amp; payment history</strong><br /><img alt="Member contribution statement" src="docs/screenshots/member/02-contribution-statement.png" width="420" /></td>
  </tr>
  <tr>
    <td valign="top"><strong>Events calendar</strong><br /><img alt="Member events calendar" src="docs/screenshots/member/03-events.png" width="420" /></td>
    <td valign="top"><strong>Optional private assistant</strong><br /><img alt="Private assistant" src="docs/screenshots/member/05-private-assistant.png" width="420" /></td>
  </tr>
</table>

### Treasurer — money that can be audited

The treasurer workspace turns validated income and recorded expenses into an annual
budget, with one-click Excel, PDF and share-ready exports.

<table>
  <tr>
    <td width="50%" valign="top"><strong>Annual budget &amp; live charts</strong><br /><img alt="Treasury workspace" src="docs/screenshots/treasurer/02-finance-workspace.png" width="420" /></td>
    <td width="50%" valign="top"><strong>Receipt declaration &amp; validation</strong><br /><img alt="Receipt declaration" src="docs/screenshots/treasurer/03-receipt-declarations.png" width="420" /></td>
  </tr>
</table>

### Secretary general — official records and communication

The secretary manages documents, policies and announcements without touching finance or
discipline.

<table>
  <tr>
    <td width="50%" valign="top"><strong>Records workspace</strong><br /><img alt="Secretary workspace" src="docs/screenshots/secretary/01-overview.png" width="420" /></td>
    <td width="50%" valign="top"><strong>Document management</strong><br /><img alt="Secretary documents" src="docs/screenshots/secretary/02-documents.png" width="420" /></td>
  </tr>
</table>

### President — executive oversight without overreach

The president gets a cross-module cockpit and full member administration, with a clear
read-only posture for sensitive actions.

<table>
  <tr>
    <td width="50%" valign="top"><strong>Governance cockpit</strong><br /><img alt="President governance cockpit" src="docs/screenshots/president/02-governance-cockpit.png" width="420" /></td>
    <td width="50%" valign="top"><strong>Member administration</strong><br /><img alt="Member management" src="docs/screenshots/president/03-member-management.png" width="420" /></td>
  </tr>
  <tr>
    <td valign="top"><strong>Operations journal</strong><br /><img alt="Operations journal" src="docs/screenshots/president/04-operation-journal.png" width="420" /></td>
    <td valign="top"><strong>Backup &amp; recovery centre</strong><br /><img alt="Backup and recovery centre" src="docs/screenshots/president/05-recovery-center.png" width="420" /></td>
  </tr>
</table>

### Oversight roles — discipline, audit and sport

<table>
  <tr>
    <td width="50%" valign="top"><strong>Auditor — read-only finance</strong><br /><img alt="Auditor finance" src="docs/screenshots/oversight/01-auditor-finance.png" width="420" /></td>
    <td width="50%" valign="top"><strong>Censor — confidential discipline</strong><br /><img alt="Censor discipline workspace" src="docs/screenshots/oversight/02-censor-discipline.png" width="420" /></td>
  </tr>
  <tr>
    <td valign="top"><strong>Sports manager — programme coordination</strong><br /><img alt="Sports workspace" src="docs/screenshots/oversight/03-sports-workspace.png" width="420" /></td>
    <td valign="top"><strong>Account security — MFA &amp; sessions</strong><br /><img alt="Account security" src="docs/screenshots/oversight/04-account-security.png" width="420" /></td>
  </tr>
</table>

### Mobile &amp; PWA — installable on a phone

The same surfaces adapt to phone widths with bottom navigation, safe-area handling and an
installable Progressive Web App shell.

<table>
  <tr>
    <td width="25%" valign="top"><strong>Member dashboard</strong><br /><img alt="Mobile member dashboard" src="docs/screenshots/mobile/01-member-dashboard.png" width="200" /></td>
    <td width="25%" valign="top"><strong>Contribution statement</strong><br /><img alt="Mobile contribution statement" src="docs/screenshots/mobile/02-member-contribution-statement.png" width="200" /></td>
    <td width="25%" valign="top"><strong>Treasury workspace</strong><br /><img alt="Mobile treasury workspace" src="docs/screenshots/mobile/03-treasurer-finance.png" width="200" /></td>
    <td width="25%" valign="top"><strong>Governance cockpit</strong><br /><img alt="Mobile governance cockpit" src="docs/screenshots/mobile/04-president-governance.png" width="200" /></td>
  </tr>
</table>

<details>
<summary><strong>See the full screenshot gallery (sign-in, announcements, tenant shells)</strong></summary>
<br />

<table>
  <tr>
    <td width="50%" valign="top"><strong>Multilingual sign-in</strong><br /><img alt="Kairo sign-in" src="docs/screenshots/public/02-login.png" width="420" /></td>
    <td width="50%" valign="top"><strong>Association announcements</strong><br /><img alt="Member announcements" src="docs/screenshots/member/04-announcements.png" width="420" /></td>
  </tr>
</table>

Screenshots are reproducible with `node scripts/capture-readme-screenshots.mjs` and the
source manifest lives in [`docs/screenshots/MANIFEST.md`](docs/screenshots/MANIFEST.md).
</details>

## What Kairo does

Kairo is a multilingual, multi-tenant application for the day-to-day administration of an
association. It keeps sensitive decisions on the server, gives each elected role a focused
workspace, and works cleanly on desktop and mobile browsers.

| Area | Included capabilities |
| --- | --- |
| Members | Registration, member search, profiles, lifecycle controls, address and contact records |
| Treasury | Contributions, non-member income, expenses, validation queues, custody tracking, exports and budget views |
| Governance | Role-aware dashboards, documents, policies, announcements, events and an understandable operations journal |
| Discipline | Confidential disciplinary files, sanction history and explicit read/write boundaries |
| Continuity | Encrypted backups, integrity checks, scheduled snapshots, recovery centre and PostgreSQL WAL archiving |
| Notifications | In-app inbox, opt-in Web Push and audited delivery workflow |
| Private AI | Optional local Ollama/Qdrant runtime behind a signed gateway; the cloud core can run without it |

## Features

### Association operations

- Member registration with automatic member codes, structured address, contribution type and optional immediate access.
- Progressive member search by name, surname, member code, phone number or email.
- Read-only member detail panel with authorised contribution and disciplinary history.
- Member lifecycle controls: edit, pause, reactivate and, for authorised roles, delete.
- Assisted access recovery for the president, vice president, secretary general and principal administrator, with a time-limited one-time password, forced replacement and session revocation.
- Events, announcements, governance documents and policy management.

### Treasury and accountability

- Individual and family contributions, partial payments and member balance statements.
- Receipt declarations for contributions, donations, sponsorships, tournament income and other revenue.
- Treasurer-only validation, rejection with reason, custody handover follow-up and configurable reminders.
- Treasurer-only expense recording with categorised annual budget impact.
- Finance audit workspace, operations journal and exports to Excel, PDF and WhatsApp-ready summaries.
- Responsive budget charts separating income sources from expenditure categories.

### Governance and discipline

- Dedicated workspaces for the president, vice president, secretary general, treasurer, auditor, censor and sports manager.
- Explicit server-enforced read/write boundaries for confidential disciplinary records.
- Complete sanction records: member, policy, circumstances, amount, status, dates and auditable changes.
- Human-readable operations journal with actor identity, role, result and action details.

### Experience and notifications

- French-first interface with English and German alternatives.
- Responsive desktop and mobile layouts, bottom navigation and installable PWA support.
- Accessible confirmation, warning and error notifications with field-level validation feedback.
- Tenant-isolated inbox, opt-in Web Push and audited delivery outcomes for important operations.

### Reliability and privacy

- Multi-tenant isolation and backend-owned capability checks.
- Optional private AI assistant with tenant- and scope-filtered retrieval.
- Core deployment can run without the local AI machine.
- Encrypted, signed and SHA-256 verified backups, daily scheduling, WAL archiving and isolated restore procedures.

## Architecture

```mermaid
flowchart LR
  Browser["Browser / PWA\nVue 3 · TypeScript · Pinia"] --> Edge["Cloudflare\nHTTPS & Tunnel"]
  Edge --> Web["Web gateway\nNginx"]
  Web --> API["FastAPI\nModular monolith"]

  API --> PG[(PostgreSQL)]
  API --> Redis[(Redis)]
  API --> Storage[(MinIO / S3)]
  API --> Worker["Celery worker & scheduler"]
  Worker --> PG
  Worker --> Storage

  API -. "optional signed request" .-> AIGateway["Private AI gateway\nlocal machine"]
  AIGateway --> Ollama["Ollama"]
  AIGateway --> Qdrant[(Qdrant)]
```

The backend is a **modular monolith**: thin routers, service orchestration and isolated
repositories. Every tenant-scoped query carries `tenant_id`, and retrieval filtering runs
*before* any context reaches a model.

### Deployment modes

```mermaid
flowchart TB
  Core["Core deployment\nweb · API · PostgreSQL · Redis · MinIO · workers"]
  Tunnel["Cloudflare Tunnel\napp.example.org"] --> Core
  Core -. "AI enabled" .-> LocalTunnel["Optional private tunnel"]
  LocalTunnel --> LocalAI["Local AI runtime\nAI gateway · Ollama · Qdrant"]
  Core --> Backup["Encrypted backups\nS3-compatible external destination"]
```

- **Core only:** a complete association platform without chat or local models.
- **Core + local AI:** the private AI runtime remains on a controlled machine; no Ollama or Qdrant port is exposed to the browser.
- **Local development:** a single Docker Compose stack for rapid iteration.

## Tech stack

| Layer | Technology |
| --- | --- |
| Web client | Vue 3, TypeScript, Pinia, Vue Router, Vite, Bootstrap, PWA |
| Native client | Flutter (Android and Web first, iOS/desktop architecture-ready) |
| API | Python 3.12, FastAPI, SQLAlchemy, Pydantic, Alembic |
| Data & jobs | PostgreSQL, Redis, Celery worker and scheduler |
| Object storage | MinIO / S3-compatible |
| Private AI (optional) | Signed AI gateway, Ollama, Qdrant |
| Delivery | Docker Compose, Nginx, Cloudflare Tunnel |
| Quality | pytest, ruff, mypy, vue-tsc, Playwright, flutter analyze/test, gitleaks, GitHub Actions |

## Security and data boundaries

- Backend-owned authorisation: the client never grants a permission by itself.
- Tenant filtering is applied to every tenant-scoped query.
- The AI retrieval filter is resolved before any context reaches a model.
- Role actions, finance decisions and recovery operations are audit logged.
- Backups are encrypted, signed, SHA-256 verified and restorable in an isolated environment.
- CI runs a secret scanner and rejects committed databases, backups and sensitive exports.

## Role workspaces

The association workflow is built around elected roles. The emergency `principal_admin`
account is an operational maintenance account, not an association office role.

| Role | Focus |
| --- | --- |
| President | Executive overview, member administration, finance and governance visibility |
| Vice president | Delegated oversight, member visibility and receipt declaration |
| Secretary general | Member administration, documents, policies, announcements and read-only discipline visibility |
| Treasurer | Financial records, receipt validation, custody follow-up, expenses and exports |
| Auditor | Read-only financial oversight and exports |
| Censor | Confidential disciplinary records and sanction management |
| Sports manager | Sports events and programme coordination |
| Ordinary member | Personal profile, contribution status, permitted documents, events and announcements |

## Quick start

### Local development

Prerequisites: Docker Desktop, Docker Compose and Git.

```powershell
git clone https://github.com/VirgileDjimgou/Kairo.git kairo
Set-Location kairo
Copy-Item .env.example .env
docker compose up --build
```

Seed the local demo data in a second terminal:

```powershell
docker compose exec api python -m app.db.seed
```

Then open:

- Web client: [http://localhost:5173](http://localhost:5173)
- API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### Core deployment without AI

```powershell
Copy-Item .env.core.example .env.core
docker compose --env-file .env.core -f docker-compose.core.yml up -d --build
```

### Optional private AI runtime

```powershell
Copy-Item .env.ai-local.example .env.ai-local
docker compose --env-file .env.ai-local -f docker-compose.ai-local.yml --profile ai-tunnel up -d --build
```

The AI gateway validates a signed, short-lived server request. When the local runtime is
unavailable, Kairo keeps the core platform available and reports the AI state clearly.

## Project layout

```text
kairo/
├── apps/web/                 Vue 3 client and PWA
├── apps/flutter_kairo/       Parallel Flutter client (Android and Web first)
├── services/api/             FastAPI modular monolith and workers
├── docs/                     Architecture, operations and validation guides
├── scripts/                  Docker, deployment and recovery helpers
├── seed/                     Local demonstration data
├── constitution/             Product and security principles
└── docker-compose*.yml       Local, core and optional-AI deployment modes
```

## Quality checks

```powershell
# Backend
python -m pytest services/api/tests -q
python -m ruff check services/api/app/ services/api/tests/
python -m mypy --config-file services/api/pyproject.toml --explicit-package-bases services/api/app/

# Frontend
Set-Location apps/web
npm ci
npm run type-check
npm run build
npm run test:e2e:locale
npm run test:e2e:roles
Set-Location ../..

# Flutter client
Set-Location apps/flutter_kairo
flutter analyze
flutter test
Set-Location ../..

# Repository guards
node scripts/check-sensitive-files.mjs
node scripts/check-i18n-coverage.mjs
node scripts/check-api-collection-paths.mjs
```

For the maintained validation commands and responsive checks, see [`docs/operations/validation-baseline.md`](docs/operations/validation-baseline.md).

## Project status and roadmap

Kairo is an active portfolio project. The Vue 3 PWA is the production client; the Flutter
Android/Web client is tracked separately and consumes the same API contracts.

- Vue 3 PWA — production client.
- Flutter client — functional parity reached through release-readiness work; Android and Flutter Web are the release targets.
- iOS and desktop — architecture-ready, deliberately deferred.

See [`PROJECT_STATUS.md`](PROJECT_STATUS.md), [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md) and
[`docs/flutter/FLUTTER_APP_ROADMAP.md`](docs/flutter/FLUTTER_APP_ROADMAP.md) for the current state.

## Documentation

- [Deployment guide](docs/deployment-guide.md)
- [Frontend architecture](docs/FRONTEND_ARCHITECTURE.md)
- [Design system](docs/DESIGN_SYSTEM.md)
- [Responsive test report](docs/RESPONSIVE_TEST_REPORT.md)
- [Flutter client roadmap](docs/flutter/FLUTTER_APP_ROADMAP.md)
- [Flutter feature parity matrix](docs/flutter/FEATURE_PARITY.md)
- [Encrypted recovery runbook](docs/operations/encrypted-recovery-runbook.md)
- [Project status](PROJECT_STATUS.md)
- [Implementation roadmap](IMPLEMENTATION_ROADMAP.md)
- [Contributing](CONTRIBUTING.md)

## License

Kairo is released under the [MIT License](LICENSE).

<div align="center">
<br />
If this project is useful or interesting, a ⭐ on GitHub is appreciated.
</div>
