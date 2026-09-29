# Kairo Roadmap V3 — Sprint 119 To Sprint 129

Status: **DRAFT — PROPOSED, NOT ACTIVE.** Sprint status is not tracked in this
file. Roadmap V2 (`docs/roadmap/KAIRO_V2_ROADMAP.md`) remains the canonical
execution roadmap until an operator explicitly activates V3.

Machine-readable companion: `docs/roadmap/KAIRO_V3_ROADMAP.json`.
Proposed on: 2026-09-27, after the completed V2 release candidate (S100–S118).

## Why a V3 cycle

V2 delivered stabilization, decomposition, contracts, observability, the module
registry and a hardened release candidate. Five classes of work remain open and
are not part of V2:

1. **Reproducibility and supply chain** — Sprint 118 found that a fresh
   production image could silently fail to start because of dependency drift
   (SQLAlchemy 2.1 dropped an unconditional `greenlet` dependency). Nothing in
   CI builds and boots the production image today.
2. **Release operations** — the remaining launch steps (Android keystore, Play
   internal testing, Flutter Web staging promotion, historical JWT rotation) are
   human-gated, but the surrounding validation and rollback rehearsals can be
   automated and rehearsed.
3. **Reliability depth** — outbox rows can be stranded in `processing` if a
   worker crashes mid-delivery; offsite backup and point-in-time recovery are
   configured but not drill-proven; the Windows host recovery path has a known
   archiving defect.
4. **Product quality depth** — remaining hardcoded strings, per-workspace
   accessibility coverage, and retention/privacy operations.
5. **Evolution decisions** — identity federation (OIDC/SAML) deserves an ADR and
   a spike before any commitment; the Flutter pilot has deferred parity items.

## Activation requirements

1. Operator approval of this draft (amendments welcome before activation).
2. `scripts/sprint-batch/roadmap.mjs` currently hardcodes
   `docs/roadmap/KAIRO_V2_ROADMAP.json`; activation must add roadmap selection or
   point it at V3.
3. `AGENTS.md` read order, aliases and `docs/automation/SPRINT_BATCH_AUTOPILOT.md`
   must reference V3; V2 becomes the historical record.
4. Start a fresh batch. V3 numbering begins at 119 so V2 completion is
   historical context, not state inheritance.

## Constraints that apply to every sprint

- preserve tenant isolation, backend-owned permissions, capability enforcement,
  audit integrity and transaction correctness;
- preserve the modular monolith (no microservices, no Kafka);
- preserve Vue PWA production viability and the Flutter client track;
- preserve API backward compatibility unless a migration is explicitly planned;
- never expose finance or disciplinary detail through push notifications;
- retrieval authorization must happen before prompt assembly;
- the LLM never decides access control and no frontend grants access;
- no tenant-scoped query may omit `tenant_id`;
- no COMBIS-specific product hardcoding;
- no destructive, store, DNS or remote-history operation without explicit human
  approval.

Objective: **REPRODUCE → RELEASE → HARDEN → VERIFY → QUALITY → EVALUATE**.

---

## Sprint 119 — Reproducible Dependency And Image Supply Chain

Phase: REPRODUCE. Dependencies: none. Gate profile: full.

**Goal:** Prevent silent dependency drift like the Sprint 118
SQLAlchemy 2.1/greenlet production-image startup blocker.

**Tasks**

- Produce a committed Python constraints lock from `requirements.txt` on the
  supported interpreter; install production images from the lock.
- Pin container base images (python:3.12-slim and the postgres/redis/minio
  references) to the digests used by the release.
- Add a CI job that builds the production api/worker image, starts api and worker
  against ephemeral postgres/redis, and asserts `/health` plus Celery readiness.
- Add dependency vulnerability scanning (`pip-audit`, `npm audit --omit=dev`)
  with a documented failing policy for critical findings.
- Document how to refresh the lock and digests.

**Acceptance**

- The production image start smoke passes in CI and locally.
- The lock installs the exact tested versions; `pip check` is clean in the image.
- A synthetic regression (removing the asyncio extra) is caught by the smoke.
- Vulnerability scanning runs in CI and its policy is documented.

---

## Sprint 120 — Release Operations Enablement

Phase: RELEASE. Dependencies: 119. Gate profile: release.

**Goal:** Turn the release-candidate runbooks into rehearsable operations while
store, DNS and secret actions stay human-approved.

**Tasks**

- Add a staging deployment validation script for the Flutter Web staging compose
  stack with an end-to-end smoke (sign-in and core navigation).
- Automate a staging rollback rehearsal: deploy, back up, restore the previous
  archive, verify smoke, keep evidence.
- Produce an operator checklist for the HUMAN_REQUIRED items: Android upload
  keystore, Play Console internal testing, Flutter Web staging hostname
  promotion, historical JWT rotation.
- Extend `pilot_acceptance_preflight.ps1` to verify release artifacts without
  printing secrets.
- Record evidence paths and approval gates under `docs/operations/`.

**Acceptance**

- Staging validation and rollback rehearsal run reproducibly and store evidence.
- The checklist covers each human gate with exact commands and rollback criteria.
- No production hostname, credential or store metadata is changed.

---

## Sprint 121 — Windows Recovery Path Parity And Archive Integrity

Phase: HARDEN. Dependencies: none. Gate profile: full.

**Goal:** Remove the Windows-host recovery caveat found in Sprint 118 and
guarantee every archive is verifiably restorable.

**Tasks**

- Replace host `tar.exe` archiving on Windows with a container-based archiver
  over the MinIO volume so archives match the Linux path.
- Verify archive integrity immediately after creation; fail the backup when
  verification fails.
- Harden `Test-KairoRecoveryDrill.ps1`: clean up extraction workspaces, exit
  non-zero on any failed step, print a compact evidence summary.
- Add a parity check comparing the Windows and Linux archive component sets.
- Update the recovery runbooks to the corrected commands.

**Acceptance**

- A Windows full backup (PostgreSQL, Redis, MinIO) is created, verified and
  restored isolated without the bsdtar failure.
- A tampered or truncated archive is rejected.
- Drill cleanup leaves no extracted operational data on disk.

---

## Sprint 122 — Outbox Crash Recovery And Stale Reclaim

Phase: HARDEN. Dependencies: none. Gate profile: backend.

**Goal:** A worker crash mid-delivery must not permanently strand outbox rows in
`processing`.

**Tasks**

- Add bounded stale reclaim for notification-outbox and domain-event rows left in
  `processing`, returning them to `pending` with a recorded reason.
- Preserve deduplication and idempotent projections; no duplicated inbox rows,
  audit projections or finance effects.
- Expose reclaimed counts through `/metrics` and `/health` details.
- Cover crash-and-recovery for both outboxes, including attempts exhaustion.
- Document recovery semantics in the operator guides.

**Acceptance**

- A stale `processing` row is retried and completed exactly once.
- Reclaiming never duplicates notifications, audit entries or payments.
- Metrics and health expose reclaimed counts safely.

---

## Sprint 123 — Offsite Backup And Point-In-Time Recovery Validation

Phase: HARDEN. Dependencies: 121. Gate profile: release.

**Goal:** Prove recovery beyond local disk: offsite destination and WAL
point-in-time recovery into an isolated target.

**Tasks**

- Automate the external S3-compatible upload against a configured endpoint only;
  fail closed when unconfigured and document the operator step.
- Add a WAL/PITR drill restoring to a chosen timestamp in an isolated container
  with schema and row-count verification.
- Schedule a periodic non-destructive drill (Celery beat) recording privacy-safe
  evidence in the tenant recovery centre.
- Validate archive and WAL retention/rotation with counts only.
- Update the encrypted recovery runbook with tested commands.

**Acceptance**

- Offsite upload and retrieval succeed against a locally emulated S3 endpoint.
- The PITR drill restores to a target timestamp and passes integrity checks.
- The recovery centre shows the latest drill evidence.

---

## Sprint 124 — Full-Stack Integration Smoke Track

Phase: VERIFY. Dependencies: 120. Gate profile: full.

**Goal:** Add a real-stack integration layer between backend tests and the mocked
browser packs.

**Tasks**

- Compose an integration environment (postgres, redis, minio, api, worker, web)
  with a deterministic seed.
- Add an HTTP/browser smoke suite covering sign-in for every canonical role,
  tenant-isolation assertions, one finance lifecycle, one disciplinary read, the
  notification inbox and module toggles.
- Run it on a schedule and on demand; document runtime and resource use.
- Produce downloadable failure evidence without exposing secrets.

**Acceptance**

- The suite passes against the real stack and fails when a seeded role boundary
  is broken.
- No mocked API responses are used in this track.
- Failure evidence artifacts are produced.

---

## Sprint 125 — Internationalization Completion

Phase: QUALITY. Dependencies: none. Gate profile: web.

**Goal:** Close the remaining translation gap and make the coverage guard
enforcing.

**Tasks**

- Move every remaining hardcoded user-facing string reported by
  `check-i18n-coverage.mjs` into FR/EN/DE catalogs or the view copy pattern.
- Remove residual inline locale ternaries tracked since Sprint 108.
- Convert `check-i18n-coverage.mjs` from informational to a failing gate with a
  shrinking allowlist.
- Keep backend enum values untranslated and preserve locale parity.

**Acceptance**

- `check-i18n-coverage.mjs` exits non-zero with an empty (or documented tiny)
  allowlist.
- FR/EN/DE parity holds for all catalogs and view copy objects.
- The locale, role and release-candidate browser packs stay green.

---

## Sprint 126 — Accessibility Depth And Role-Workspace Coverage

Phase: QUALITY. Dependencies: none. Gate profile: full.

**Goal:** Extend the Sprint 118 audit from the shell to every role workspace and
add a repeatable manual protocol.

**Tasks**

- Run and fix axe WCAG 2.2 AA findings for every workspace reachable by the
  canonical roles at 320/390/1280 widths.
- Add Flutter accessibility tests for the role shell, finance, discipline and
  inbox surfaces at 200% text scaling and dark mode.
- Define a manual screen-reader protocol (NVDA, Android TalkBack) and record a
  pilot pass.
- Add focus-order and keyboard-only journey checks for main office workflows.

**Acceptance**

- The accessibility pack covers all role workspaces and passes.
- The manual protocol is documented with results for one office role and one
  member role.
- No regression in the locale, role or release-candidate packs.

---

## Sprint 127 — Data Retention And Privacy Operations

Phase: QUALITY. Dependencies: none. Gate profile: backend.

**Goal:** Tenant-scoped retention and privacy operations that are auditable and
never bypass authorization.

**Tasks**

- Add configurable per-tenant retention windows for audit events, notification
  history, chat conversations and ingestion logs.
- Implement member personal-data export and erasure online in the backend,
  audited and role-restricted.
- Keep statutory finance and disciplinary records out of erasure scope unless
  legally allowed; document the retention matrix.
- Add tests for tenant isolation, audit entries and role restrictions.
- Run retention in the worker with idempotent, privacy-safe counts.

**Acceptance**

- Retention tasks run in the worker, are idempotent and log counts only.
- Export and erasure are backend-only, role-gated, audited and tested.
- Documentation states what is retained and why.

---

## Sprint 128 — Identity Federation Evaluation

Phase: EVALUATE. Dependencies: none. Gate profile: backend.

**Goal:** Decide, with evidence, whether OIDC/SAML federation belongs in the
product and how it preserves tenant isolation.

**Tasks**

- Write an ADR evaluating OIDC/SAML against the identity module: provider
  abstraction, tenant mapping, role claims, session implications.
- Build a spike against a local OIDC provider behind a never-default feature
  flag.
- Document threat-model impacts: token validation, replay, logout, MFA, recovery.
- Produce a go/no-go recommendation with estimated effort; no production
  enablement in this sprint.

**Acceptance**

- The ADR exists with a clear recommendation and rejected alternatives.
- The spike demonstrates login mapping in the test environment only.
- No production behaviour changes while the flag is off.

---

## Sprint 129 — Flutter Pilot Completion

Phase: RELEASE. Dependencies: 120. Gate profile: release.

**Goal:** Finish deferred pilot items so the Flutter client can enter a
controlled internal-testing pilot.

**Tasks**

- Implement permanent member deletion parity behind the president/secretary role
  gate with confirmation, consuming the existing API only.
- Prepare Play Console internal-testing assets: signed AAB checklist, store
  listing text FR/EN/DE, data-safety answers.
- Validate iOS/desktop architecture readiness with build checks and no release
  commitment.
- Update `docs/flutter/FEATURE_PARITY.md` and the Flutter `PROJECT_STATUS.md`.

**Acceptance**

- Member deletion works through the API with role tests and updates the parity
  matrix.
- Internal-testing assets are prepared; signing and store actions remain
  operator-gated.
- iOS/desktop checks are documented as non-release validation.
