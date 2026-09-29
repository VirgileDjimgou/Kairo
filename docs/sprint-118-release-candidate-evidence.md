# Sprint 118 — Release Candidate Evidence

Date: 2026-09-27
Sprint: Roadmap V2 Sprint 118 — Product Hardening And Release Candidate
Operator: Agentic AI (opencode), Windows workstation + Docker core stack

This record is the auditable evidence for the release-candidate acceptance
criteria: automated gates, restore drill, upgrade path, rollback path,
notification recovery, secret hygiene, and an end-to-end demonstration.

## 1. Regression matrix

| Gate | Command | Result |
| --- | --- | --- |
| Backend tests | `python -m pytest services/api/tests -q` | 362 passed (359 + 3 new recovery tests) |
| Backend lint | `python -m ruff check services/api/app/ services/api/tests/ --ignore E501` | clean |
| Backend types | `python -m mypy --config-file services/api/pyproject.toml --explicit-package-bases services/api/app/` | 301 files, no issues |
| Web build | `cd apps/web && npm run build` | type-check + production build pass |
| Web locale pack | `npm run test:e2e:locale` | 20 passed |
| Web role pack | `npm run test:e2e:roles` | 17 passed |
| Web release-candidate pack | `npm run test:e2e:release-candidate` | 9 passed |
| Web accessibility pack | `npm run test:e2e:a11y` | 6 passed |
| Flutter analyze | `apps/flutter_kairo/scripts/flutter.ps1 analyze` | no issues |
| Flutter tests | `flutter.ps1 test` | 52 passed (50 + 2 new accessibility tests) |
| Flutter format | `dart format --set-exit-if-changed lib test` | clean after reformatting `contract_parity_test.dart` |
| Flutter Web build | `flutter build web --dart-define=KAIRO_FLAVOR=production ...` | built |
| Flutter Android debug | `flutter build apk --debug --dart-define=KAIRO_FLAVOR=production ...` | built |
| Contracts | `npm run contracts:check` | OpenAPI stable, generated TS/Dart current, route coverage OK |
| Guards | `check-sensitive-files`, `check-i18n-parity`, `check-api-collection-paths`, `check-capability-bundles` | pass |

Performance (`npm run perf:check`) remains an opt-in check with committed
statement-count thresholds; it is unchanged by this sprint.

## 2. Release blocker found and fixed

A fresh production image build failed to start:

```text
ImportError: The SQLAlchemy asyncio module requires that the Python 'greenlet'
library is installed.
```

- Root cause: `services/api/requirements.txt` allowed `sqlalchemy>=2.0.36,<3.0.0`.
  A current resolution installed SQLAlchemy 2.1.x, which no longer pulls
  `greenlet` unconditionally, so both `api` and `worker` containers crashed on
  import. The tested workstation baseline is SQLAlchemy 2.0.x.
- Fix: `sqlalchemy[asyncio]>=2.0.36,<2.1.0`. The `[asyncio]` extra guarantees
  `greenlet`; the bound keeps the release on the tested 2.0 series.
- Verification: rebuilt images contain `greenlet 3.5.6` and `SQLAlchemy 2.0.54`;
  `api` and `worker` start, migrations run, `/health` returns HTTP 200, and the
  Celery worker reports `ready`.

## 3. Upgrade path (deployed schema → release head)

The local core deployment database was at Alembic revision `0029` before the
sprint. The release head is `0033`.

1. Pre-migration safety backup: `pg_dump --format=plain --clean --if-exists
   --create` of the `0029` database, archived on the host (the PostgreSQL payload
   was verified by the rollback drill in section 5; the MinIO portion of that
   host archive hit the Windows tar limitation documented there).
2. `alembic upgrade head` applied `0030 → 0031 → 0032 → 0033` inside the
   production image.
3. Verified `alembic current` = `0033 (head)`.
4. Data preserved before/after: tenants 1, users 125, members 127, contributions
   121, expenses 4, sanctions 3, audit events 494.
5. `/health` after the upgrade reports `database: ok`, `backup: ok`,
   `notification_outbox: ok`, `domain_event_outbox: ok` (the pre-upgrade database
   reported `domain_event_outbox: unavailable`, which the migration resolved).

Operational note: the application-level encrypted backup CLI cannot run against
an older schema because the newer code expects columns added by `0030+`. The
upgrade helper already uses the infrastructure-level `scripts/backup.sh`; the
runbook now states this explicitly. Backup before migration must use the
infrastructure path.

## 4. Restore drill (non-destructive)

Executed with the supported encrypted pipeline:

```powershell
.\scripts\Test-KairoRecoveryDrill.ps1 `
  -ArchiveName "kairo-recovery-20260927T195252Z-f300328b.enc" `
  -EnvironmentFile ".env.core"
```

Result: PASSED.

- Encrypted archive and signed manifest verified (SHA-256 + signature).
- Payload extracted into an isolated recovery workspace.
- PostgreSQL restored into a disposable `postgres:16-alpine` container with no
  connection to the primary stack; the container was removed afterwards.
- Restored counts: members 127, contributions 121, sanctions 3, expenses 4 —
  identical to the source database.

## 5. Rollback drill

The pre-migration safety dump was restored into an isolated `postgres:16-alpine`
container:

- database revision after restore: `0029` (the pre-upgrade state);
- counts identical to the source (tenants 1, users 125, members 127,
  contributions 121, audit 494);
- the isolated container was destroyed afterwards; no production data was
  touched.

Windows host caveat discovered: the bundled `tar.exe` (bsdtar) crashes
(`0xC0000005`) when archiving the live MinIO data tree, producing a truncated
archive. Windows operators must use `scripts/Backup-Kairo.ps1`
(container-side encrypted archive) or the container-based archiver, and verify
archives with `tar -tzf` when the raw host path is used. This does not affect the
Linux `scripts/backup_core.sh` path used by the deploy helper.

## 6. Notification recovery validation

Design guarantee: inbox rows are written in the business transaction
(domain-event handlers dispatch inline); Celery only processes push delivery.
Validated by new tests in `services/api/tests/test_notification_convergence.py`:

| Scenario | Test | Assertion |
| --- | --- | --- |
| Worker/Celery outage | `test_worker_outage_defers_delivery_but_preserves_business_state` | Business state and outbox persist with no inbox duplication; delivery converges exactly once after the worker returns. |
| Web Push/Firebase outage | `test_push_provider_outage_keeps_the_inbox_and_contains_the_failure` | Three bounded attempts, event completes, inbox durable, `failure_count` increments, no duplicates. |
| Unexpected provider exception | `test_unexpected_provider_exception_is_contained_as_a_transient_failure` | The outbox maps the exception to a transient failure instead of wedging the queue. |

The one defensive code change: `_send_with_retry` now converts an unexpected
provider exception into `PushOutcome.TRANSIENT`, so a provider library failure
can never abort an outbox event. The real providers already catch exceptions and
return outcomes; this guards the boundary.

## 7. Accessibility

See `docs/operations/accessibility-audit.md`. Summary: axe-core WCAG 2.2 AA packs
pass at 320 px phone and desktop widths for public and authenticated surfaces, a
localized skip link and named progress bars were added, contrast was fixed
app-wide for subtle badges and kickers, and Flutter covers 200% text scaling and
dark mode.

## 8. Secret hygiene

- `node scripts/check-sensitive-files.mjs`: 1226 tracked files checked, pass.
- `.env*` files and `backups/` are ignored; no credential file is tracked.
- Firebase is not configured in the repository; the doctor prints presence only.
- CI retains the gitleaks history scan. The only open history item is the
  documented `HUMAN_REQUIRED` JWT rotation tracked in
  `docs/security/HISTORY_EXPOSURE_REPORT.md`.

## 9. End-to-end release-candidate demonstration

Against the freshly built production images and the real local PostgreSQL data:

- `POST /api/v1/auth/login` with the seeded `admin@demo.org` returned a JWT
  containing 38 capabilities (including Sprint 117 module/role-bundle
  capabilities).
- `GET /api/v1/auth/me` returned the authenticated principal with roles
  `admin`, `principal_admin`.
- `GET /api/v1/modules` returned the tenant/capability-filtered module registry.
- `GET /api/v1/memberships/?limit=1` returned HTTP 200 under tenant scope.
- `GET /api/v1/notifications/health` reported `worker_running: true`, empty
  outbox, and configured Web Push/Firebase transports.

## 10. Known limitations and follow-ups

- Permanent member deletion remains deferred in the Flutter pilot; the PWA is
  the controlled fallback (`docs/flutter/FEATURE_PARITY.md`).
- Hardcoded strings remain in a shrinking set of admin Vue views; the i18n
  coverage report is informational and tracked, not a release blocker.
- Manual screen-reader and physical-device accessibility passes remain part of
  the pilot checklist.
- The historical JWT secret rotation remains `HUMAN_REQUIRED`.
- Android/Cloudflare production promotion stays a human approval boundary.
