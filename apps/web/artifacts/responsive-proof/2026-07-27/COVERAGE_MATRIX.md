# Kairo responsive proof matrix — 2026-07-27

## Visual evidence

| Platform | Engine | Viewports | Routes / areas | Result |
|---|---|---|---|---|
| Android simulation | Chromium | 320×568, 360×800, 390×844, 412×915, 430×932 | members plus the representative route matrix below | PASS |
| iOS simulation | WebKit | 375×812, 390×844, 393×852, 430×932 | finance audit cards | PASS |
| Desktop regression | Chromium | 1280×720, 1440×900, 1920×1080 | members desktop table | PASS |
| Cloudflare production | Chromium + WebKit | Pixel 5, iPhone 13 | public login | PASS |

Representative Android routes inspected at 390×844:

- `/admin`
- `/admin/members`
- `/admin/contributions`
- `/admin/access`
- `/admin/disciplinary`
- `/admin/events`
- `/admin/announcements`
- `/admin/audit`
- `/finance-audit`
- `/censor`
- `/members/profile`
- `/account/security`
- `/chat`

## Roles

The role-driven navigation suite exercised:

- `principal_admin`
- `admin`
- `president`
- `vice_president`
- `secretary_general`
- `treasurer`
- `auditor`
- `censor`
- `sports_manager`
- `member`

Screenshot evidence contains authenticated mock sessions for `principal_admin`, `auditor`, `censor`, and `member`. No physical Android or iOS device was used; Android is Chromium simulation and iOS is WebKit simulation.

## Counts

- Before screenshots supplied by the user: 17
- Android proof screenshots: 17
- iOS proof screenshots: 4
- Desktop regression screenshots: 3
- Cloudflare production screenshots: 2
- Pending screenshots: 0

