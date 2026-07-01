# Project State

Last verified against repository code on 2026-07-01.

## Product Snapshot

Kairo, also positioned as OrgMind AI, is a local-first multi-tenant RAG platform for organizations.

The current roadmap extension through Sprint 40 is complete. The repository is in a portfolio-ready, open-source handoff state, and any further work should begin with a new roadmap.

## Implemented Sprints

- Sprint 0: Foundation and repository skeleton
- Sprint 1: Identity, tenancy, and JWT auth
- Sprint 2: Professional Vue layout
- Sprint 3: Document upload and object storage
- Sprint 4: Ingestion worker and parsing
- Sprint 5: Embeddings and Qdrant indexing
- Sprint 6: First RAG chat
- Sprint 7: Admin RAG controls
- Sprint 8: Membership and contributions
- Sprint 9: Policies, rules, and discipline
- Sprint 10: Events and announcements
- Sprint 11: Cloudflare Tunnel Deployment
- Sprint 12: Evaluation and AI Safety
- Sprint 13: Demo Tenant and Portfolio Polish
- Sprint 14: Multi-Channel Extensions
- Sprint 15: Commercialization Baseline
- Sprint 16: Tenant Activation And Multi-Tenant UX
- Sprint 17: Identity Lifecycle And Access Hardening
- Sprint 18: Module Enforcement And Entitlements
- Sprint 19: Audit Trail And Administrative Governance
- Sprint 20: Document Operations Maturity
- Sprint 21: Data Import And Backoffice Automation
- Sprint 22: Product UX Polish And Browser QA
- Sprint 23: Observability And Runtime Reliability
- Sprint 24: Production Validation, Recovery And Security Hardening
- Sprint 25: Commercial Packaging And Launch Readiness
- Sprint 26: Public Product Landing And Lead Capture
- Sprint 27: Guided Tenant Onboarding And Conversion Flow
- Sprint 28: Admin Overview And Tenant Operations Hub
- Sprint 29: Team Invitations And Access Operations Console
- Sprint 30: Account Security And Identity Self-Service
- Sprint 31: Secure Identity Message Delivery And Access Notifications
- Sprint 32: Session Governance And Security Event Operations
- Sprint 33: Tenant User Lifecycle Governance And Account Lockdown
- Sprint 34: Authentication Hardening And Recovery Stability
- Sprint 35: Operational Reliability, Data Safety, And Migration Discipline
- Sprint 36: Association Operations Robustness
- Sprint 37: Final Open-Source Release Stabilization And Portfolio Readiness
- Sprint 38: Treasurer Workspace Activation And Finance Permission Hardening
- Sprint 39: Role-Aware Dashboard And Action Surface Hardening
- Sprint 40: Demo Gallery And Handoff Polish

## Current State

- **Open-source release**: v0.1.0
- **Current roadmap extension**: complete through Sprint 40
- **Backend tests**: 181 pass, 0 failures
- **Frontend build**: clean
- **License**: MIT

## Next Steps

The current roadmap is complete.
Future work should begin with a new roadmap before any new sprint work starts.

## Known Limitations

- Only email is wired for real identity delivery (Telegram/WhatsApp are simulated placeholders)
- Production Docker builds still benefit from occasional end-to-end validation with Docker
- Cloudflare Tunnel setup is documented but not validated with a real tunnel integration test
- Backup script is bash-only and may need adaptation for Windows/macOS Docker Desktop
- LLM responses depend on Ollama model availability
