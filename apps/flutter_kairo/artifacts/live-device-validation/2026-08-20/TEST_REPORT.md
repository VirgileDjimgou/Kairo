# Live validation report — 2026-08-20

## Infrastructure

- Docker Core started with the Cloudflare Tunnel profile.
- Public HTTPS smoke validation passed: 6/6 (`/health`, `/metrics`, root page, and API documentation protection).
- PostgreSQL and Redis reported healthy; API, worker, scheduler, MinIO, web gateway, and cloudflared were running.
- The optional local AI runtime was intentionally disabled. This is expected and does not disable association modules.
- Firebase Admin credentials were present, readable, and validated without delivering a message.

## Automated security and role checks

- API release, capability, tenant-isolation, notification, receipt, expense, and disciplinary tests: 56 passed.
- Flutter test suite: 45 passed.
- Vue 3 type check: passed.

The API tests use an isolated temporary SQLite database. They cover member, secretary general, treasurer, auditor, censor, sports manager, president, vice president, and principal administrator permission boundaries without mutating association data.

## Android physical-device validation

- Samsung SM-G975F was detected through Wi-Fi ADB.
- The initially installed APK targeted `127.0.0.1:8080`; a production-configured replacement was built and installed against `https://app.combissportverein.org/api/v1`.
- The `secretary_general` test account authenticated successfully on the physical Samsung and rendered the role dashboard.
- Android notification activation succeeded in the app. The server stored one active Firebase token for the secretary account (length 142; failure count 0).
- A deliberately labelled, non-business FCM validation notification was queued, delivered by Firebase, visibly displayed in the Android notification shade while the app was in the background, and recorded in the authenticated inbox.
- Tapping a test notification with target `/members` opened the members screen on the physical phone.
- The target path `/notifications` is mapped to the Flutter inbox destination.
  Regression coverage is maintained in `test/sprint_f9_release_readiness_test.dart`.
- The documented member accounts are absent from the current database. The president account is active but its documented test password is no longer valid; it was not reset during validation.

## Evidence

- `01-launch-current.apk.png` — physical Samsung login surface.
- `02-president-login.png` — detected loopback API configuration failure.
- `02-president-login.log.txt` — Android transport evidence showing the loopback connection attempt.
- `03-production-apk-login.png` — production-configured APK login surface on the Samsung.
- `08-secretary-authenticated.png` — authenticated secretary dashboard on the Samsung.
- `11-fcm-activation-result.png` — in-app confirmation that Android notifications were enabled.
- `13-fcm-background-delivered.png` — FCM notification visibly received while Kairo was in the background.
- `15-fcm-deep-link-members.png` — notification tap opened the members screen.

## Required next physical step

Reset or provide the current test passwords for the president and an ordinary member, or explicitly authorize an isolated staging tenant. Then repeat the physical walkthrough for those two remaining role classes.
