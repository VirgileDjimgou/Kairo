# Flutter Android And Web Release Runbook

## Scope and safety boundary

This runbook prepares the separate Flutter Android/Web pilot. The Vue 3 PWA remains
the production fallback. A Flutter production promotion requires the association's
explicit approval after the staging and Play internal-testing checks below.

## 1. Verify the candidate

```powershell
Set-Location apps/flutter_kairo
.\scripts\release_check.ps1 -Flavor staging -ApiBaseUrl https://flutter-staging.combissportverein.org/api/v1
```

Record the test result, Flutter version, APK checksum and screenshot evidence at phone
and desktop widths. Test an authorised role, a restricted role, sign-out, offline
read state, a network timeout, and a push deep link. Do not use production credentials
in screenshots.

## 2. Create the private Android upload key

Run this once on a controlled operator workstation. Keep the generated `.jks` file in
a private encrypted location outside this repository.

```powershell
keytool -genkeypair -v -keystore C:\secure\kairo-upload-keystore.jks -alias kairo-upload -keyalg RSA -keysize 2048 -validity 10000
```

Copy `apps/flutter_kairo/android/key.properties.example` to
`apps/flutter_kairo/android/key.properties`, then replace every example value. The
file and keystore are ignored by Git. Losing this key prevents updates to the same
Google Play application; store an encrypted recovery copy with access restricted to
authorised operators.

## 3. Produce the internal-test bundle

```powershell
Set-Location apps/flutter_kairo
.\scripts\release_check.ps1 -Flavor staging -ApiBaseUrl https://flutter-staging.combissportverein.org/api/v1 -BuildAab
Get-FileHash build\app\outputs\bundle\release\app-release.aab -Algorithm SHA256
```

Upload `app-release.aab` only to the Play Console **Internal testing** track. Keep
`applicationId` as `org.combissportverein.kairo`; changing it creates a different
application. Increment the public version and build number for every subsequent
upload.

Prepare Play Console assets before inviting testers:

- app name, short and full descriptions;
- 512×512 icon, feature graphic and current phone screenshots;
- privacy policy URL and support contact;
- Data safety declaration: membership and finance data are processed by the
  association's API; password material is never collected by the client; FCM tokens
  are used only for opted-in notification delivery;
- internal tester group and feedback route.

## 4. Start Flutter Web staging

```powershell
docker compose --env-file .env.core -f docker-compose.core.yml up -d
docker compose --env-file .env.core -f docker-compose.flutter-web.yml up -d --build
Invoke-WebRequest http://localhost:8082/health
```

In Cloudflare Zero Trust, create a **new** public hostname such as
`flutter-staging.combissportverein.org` on the existing core tunnel. Route it to
`http://flutter-web:80`. The service proxies `/api/` internally to FastAPI so the
browser uses only HTTPS and same-origin API calls.

Verify the staging hostname on a phone and desktop browser. The existing
`app.combissportverein.org` PWA route must remain unchanged. Never configure a
production hostname without explicit written approval.

## 5. Pilot and rollback

Invite a small, known tester group. Capture role, device, app version, target URL,
steps, expected result, actual result and screenshot in the pilot feedback template.

If a release blocks sign-in, permission boundaries, receipts, finance visibility,
discipline visibility, notifications, or causes data ambiguity:

1. stop the internal-testing rollout or remove the affected test release;
2. direct users to the stable PWA at `https://app.combissportverein.org`;
3. preserve server data and audit trails; do not restore or mutate data merely to
   roll back a client;
4. reproduce the issue on staging, patch it, re-run the release checks, and upload a
   new version code.

## 6. Production promotion gate

Production promotion requires all of the following: signed AAB validated on the
internal track, staging Web validation, canonical role/tenant and phone/desktop proof,
privacy and support details approved, and explicit association approval. This runbook
does not authorise deployment by itself.
