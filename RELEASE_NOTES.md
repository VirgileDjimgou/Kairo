# Kairo v0.1.0 — Release Notes

## Overview

Kairo (OrgMind AI) is a local-first, multi-tenant RAG platform for associations, clubs, NGOs, and small businesses. This is the initial open-source release.

## What It Does

- Upload and index internal documents (PDF, DOCX, TXT, Markdown, CSV, images with OCR)
- Ask questions and get grounded answers with source citations
- Manage members, contributions, payments, and balances
- Track policies and disciplinary records
- Publish events and announcements with visibility controls
- Control access with role-based permissions and tenant isolation
- Configure module toggles, branding, and tenant settings
- Secure identity lifecycle (invitations, password reset, MFA, sessions)
- Import/export member and contribution data via CSV

## Target Audience

Self-hosted deployment for organizations of up to approximately 200 members. The entire stack runs locally via Docker Compose.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
docker compose exec api python -m app.db.seed
```

Then open http://localhost:5173. See [README.md](README.md) for details.

## Architecture

- **Frontend**: Vue 3, TypeScript, Pinia, Bootstrap 5
- **Backend**: FastAPI (Python 3.12), modular monolith
- **Database**: PostgreSQL
- **Storage**: MinIO (S3-compatible)
- **Queue/Worker**: Redis + Celery
- **Vector Store**: Qdrant
- **LLM/Embeddings**: Ollama
- **Auth**: JWT with refresh tokens, tenant-scoped sessions

## Test Coverage

239 backend integration tests (SQLite, no external infrastructure required).
Frontend type-check (`npm run type-check`) and production build (`npm run build`) pass.
Localization E2E pack (`npm run test:e2e:locale`) passes on Chromium.

## Roles And Boundaries

- **Member**: read-first self-service only (profile, balance, personal contribution
  history, personal PDF statement). Never sees another member's data.
- **Office roles**: targeted write scopes by role — treasurer (finance), secretary
  general (documents/policies/announcements), censor (discipline), sports manager
  (sports events), president/vice president (governance oversight), auditor
  (read-only finance), principal admin (broadest tenant administration).
- **Backend-only enforcement**: tenant isolation and permissions are enforced by
  the backend; the LLM never decides access and never receives unauthorized chunks.

## Known Limitations

- Only email is wired for real identity delivery (Telegram/WhatsApp are simulated placeholders)
- LLM responses depend on a locally available model (Ollama or an OpenAI-compatible server such as LM Studio)
- No SSO/SAML/OIDC integration
- No mobile app (the web UI is responsive)
- Production Docker path is validated through build and smoke checks; a full multi-host runbook is operational guidance rather than a certified deployment
- Demo tenant is fictional (Combis Sport Verein / `demo` slug) and must not be confused with a real organization

## License

MIT
