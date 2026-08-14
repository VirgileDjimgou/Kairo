# Kairo Flutter Client

Kairo Flutter is the separate Android and Web companion application for Kairo. It
uses the existing FastAPI contracts and does not replace the Vue 3 PWA, which remains
the production fallback throughout the controlled pilot.

## Supported release targets

- Android: installable package and Play Console internal test track.
- Flutter Web: separate staging hostname behind the existing Cloudflare architecture.
- iOS and desktop: architecture-ready but intentionally deferred.

## Local checks

```powershell
Set-Location apps/flutter_kairo
.\scripts\flutter.ps1 pub get
.\scripts\flutter.ps1 analyze
.\scripts\flutter.ps1 test
.\scripts\release_check.ps1 -Flavor staging -ApiBaseUrl https://flutter-staging.combissportverein.org/api/v1
```

The release check builds a Flutter Web release and Android debug APK. It never deploys
or promotes a release.

## Android signing

Release bundles are deliberately fail-closed: a private upload keystore and
`android/key.properties` are required. Copy
[`android/key.properties.example`](android/key.properties.example) to
`android/key.properties`, provide the real private values, then run:

```powershell
.\scripts\release_check.ps1 -Flavor staging -ApiBaseUrl https://flutter-staging.combissportverein.org/api/v1 -BuildAab
```

Do not commit the keystore, `key.properties`, Firebase configuration, passwords or
tokens. The full procedure is in
[`docs/flutter/RELEASE_RUNBOOK.md`](../../docs/flutter/RELEASE_RUNBOOK.md).

## Flutter Web staging

Build the separate staging service only after the core Docker stack is running:

```powershell
docker compose --env-file .env.core -f docker-compose.core.yml up -d
docker compose --env-file .env.core -f docker-compose.flutter-web.yml up -d --build
```

It is exposed locally on `http://localhost:8082`. Configure a **new staging**
Cloudflare hostname to route to `http://flutter-web:80`; do not point the existing PWA
hostname at this service without explicit production approval.

## Documentation

- [Flutter roadmap](../../docs/flutter/FLUTTER_APP_ROADMAP.md)
- [Feature parity matrix](../../docs/flutter/FEATURE_PARITY.md)
- [Release runbook](../../docs/flutter/RELEASE_RUNBOOK.md)
- [Privacy and support](../../docs/flutter/PRIVACY_AND_SUPPORT.md)
- [Pilot feedback template](../../docs/flutter/PILOT_FEEDBACK_TEMPLATE.md)
