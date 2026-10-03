# COMBIS Real-Device Pilot Checklist (Chrome Android)

Status: **PREPARED — manual real-device steps PENDING human validation.**

Prepared by Roadmap V2 Sprint 128 (Real Full-Stack Release Gate And COMBIS Pilot).
The automated portions below were validated against the real production-like stack
on 2026-10-03. The manual device steps require a physical Android device and the
COMBIS pilot environment; they have **no automated equivalent** and are therefore
explicitly pending until an operator executes and records them.

Related documents:

- `docs/pwa/PWA_ARCHITECTURE.md` — canonical Service Worker, offline and install flow
- `docs/pwa/FLUTTER_TO_PWA_PARITY.md` — capability continuity and deprecations
- `docs/notifications/NOTIFICATION_OPERATOR_GUIDE.md` — delivery operations
- `docs/pwa/TENANT_DOMAINS.md` — tenant onboarding runbook

## 1. Automated evidence already validated (Sprint 128)

The S128 release gate ran the real stack (nginx → Vue/PWA → FastAPI → PostgreSQL →
domain events → notification outbox → Celery worker → authenticated inbox) with
seeded COMBIS and Tenant X data, without API mocking:

```bash
# Deterministic production-like stack (PostgreSQL, Redis, API, Celery worker with
# embedded beat, Vue/PWA). MinIO stays operator-provisioned (see limitations).
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  up -d postgres redis
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  run --rm api alembic upgrade head
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  run --rm api python /app/scripts/seed_full_stack.py
docker compose -p kairo-release-gate \
  -f docker-compose.yml -f docker-compose.prod.yml \
  -f docker-compose.ci.yml -f docker-compose.release-gate.yml \
  up -d api worker web

KAIRO_GATE_BASE_URL=http://localhost:8080 node scripts/run-full-stack-gate.mjs
cd apps/web && KAIRO_GATE_BASE_URL=http://localhost:8080 npm run test:e2e:real
```

Validated 2026-10-03: **30/30 API/worker scenario steps** and **3/3 real browser
tests** passed.

| Area | Automated proof | Status |
| --- | --- | --- |
| Finance lifecycle | Member → secretary cash-receipt declaration → treasurer validation → payment → annual budget through the real API/database | VALIDATED |
| Domain event → outbox → worker → inbox | Treasurer `finance.receipt_declared` and declarant `finance.receipt_validated` arrive through the Celery worker | VALIDATED |
| Deep-link contract | Inbox event carries the canonical envelope with `target_path=/finance` and the domain event id | VALIDATED |
| Deep-link target route | Real browser click on the inbox item lands on the exact authorized `/finance` route | VALIDATED |
| Installation registration and revocation | `POST /notifications/devices`, preferences read/update, `revoke` disables the profile binding | VALIDATED |
| Tenant isolation | Tenant X sees only its own membership, cannot read a COMBIS member or process its receipt, receives no COMBIS finance notification | VALIDATED |
| Role authorization | Declarant cannot process their own declaration (`403`); unauthorized role cannot read the annual budget (`403`) | VALIDATED |
| Branding | `/auth/me` membership and page title carry `COMBIS App` | VALIDATED |
| Tenant manifest | `/tenants/public/combis/manifest` serves branding with ≥2 launcher icons | VALIDATED |
| Host resolution | `<slug>.<PLATFORM_BASE_DOMAIN>` and the exact custom domain resolve to COMBIS; unknown host is `404` | VALIDATED |
| Service Worker | Exactly one controlling worker; offline navigation falls back to the cached `/dashboard` shell | VALIDATED |
| Accessibility | axe-core WCAG 2.2 AA tags report zero violations on the authenticated dashboard | VALIDATED |
| FR/EN/DE and Android viewport | Document language is one of fr/en/de; 390 × 844 viewport has no horizontal overflow; sign-out returns to `/login` | VALIDATED |
| CI wiring | `.github/workflows/full-stack-release-gate.yml` runs the same steps nightly/manually with artifact upload | CONFIGURED (not yet executed in GitHub Actions) |

## 2. Manual Chrome Android checklist — PENDING

Run each step on the COMBIS pilot host with a physical Android device. Record the
device model, Android version, Chrome version, timestamp and result. Until then,
every row stays **PENDING — human validation required**.

| # | Step | Expected result | Status |
| --- | --- | --- | --- |
| M1 | Open the COMBIS host in Chrome Android and sign in as the treasurer | Branded title/favicon (`COMBIS App`); dashboard renders at phone width without horizontal scrolling | PENDING |
| M2 | Install the PWA through the in-app install CTA; confirm the launcher icon and name | Standalone app launches from the launcher with COMBIS branding; installation never requests notification permission | PENDING |
| M3 | Enable notifications explicitly in the notification bell | Permission prompt appears only from this action; subscription registers | PENDING |
| M4 | Trigger a treasurer notification (receipt declaration) and background the app | Inbox event exists after reopening | PENDING |
| M5 | **Closed-application notification**: close the installed PWA completely, then trigger a notification | System notification arrives with the generic body (no finance or disciplinary detail) | PENDING |
| M6 | **Exact deep link**: tap the system notification | App opens (or focuses) on the exact authorized target route (`/finance` for the treasurer), not the dashboard fallback | PENDING |
| M7 | **Token revocation**: sign out, then confirm the installation is revoked; trigger another notification | No further push is delivered to the revoked installation; a later sign-in re-registers | PENDING |
| M8 | **Application update**: deploy a new web build, reopen the installed PWA | Update notice appears; the app applies the update and loads the new shell without a manual cache clear | PENDING |
| M9 | **Offline behavior**: enable airplane mode, open the installed PWA | Cached application shell is served; authenticated data operations fail safely | PENDING |
| M10 | **Language and accessibility**: switch FR/EN/DE; run TalkBack through sign-in and the dashboard | All three locales render; focus order, labels, touch targets and contrast remain usable | PENDING |
| M11 | **Multi-tab and standalone**: open the notification target with two app windows and from the browser | Exactly one window focuses and navigates to the target route | PENDING |
| M12 | **Custom host**: repeat M1–M4 on the custom domain | Same branding, manifest and behavior as the platform subdomain | PENDING |

## 3. Known limitations

- **MinIO is operator-provisioned.** MinIO public images moved behind registry
  authentication in 2025; the CI gate excludes MinIO through
  `docker-compose.ci.yml` because the validated scenario does not upload
  documents. Operators must supply registry credentials or an equivalent S3
  endpoint for document workflows.
- **Android FCM requires the association's Firebase project.** The S128
  environment validates VAPID Web Push, installation registration/revocation and
  inbox delivery; native FCM delivery on a physical device remains part of the
  manual pilot (M3–M6).
- **The full-stack GitHub workflow has not yet run in GitHub Actions.** The same
  commands were validated locally against the production-like stack; the
  scheduled/manual workflow is configured with artifact upload.
- **Real-device steps are pending.** No PASS is claimed for M1–M12 until an
  operator records the evidence.

## 4. Evidence to capture

- Device model, Android version, Chrome version, pilot host and timestamp.
- Screenshots or screen recordings for M2, M5, M6, M8, M9.
- The notification payload received (must remain generic).
- The exact route opened by M6.
- Any deviation, failure or rollback decision.

## 5. Abort and rollback

Stop the pilot and return to the browser PWA if a notification exposes finance or
disciplinary detail, a deep link opens an unauthorized route, tenant isolation
fails, or the installed app serves a stale shell that cannot update. The browser
PWA remains the supported fallback; Flutter is frozen reference code (ADR-014)
and is not a pilot fallback.
