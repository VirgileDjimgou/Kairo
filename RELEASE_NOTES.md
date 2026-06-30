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

181 backend integration tests (SQLite, no external infrastructure required).
Frontend builds clean (TypeScript-checked, 234 modules).

## Known Limitations

- Only email is wired for real identity delivery (Telegram/WhatsApp are simulated)
- LLM responses depend on Ollama model availability
- No SSO/SAML/OIDC integration
- No mobile app
- Production deployment requires Docker Compose on a Linux host (see deployment guide)

## License

MIT
