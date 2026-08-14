# Kairo Flutter 1.0.0-rc.2

## Candidate scope

- Role-aware association operations for Android and Flutter Web.
- Member, receipt, finance, governance, discipline, notifications and optional AI
  surfaces, all backed by existing FastAPI permissions.
- Identity-scoped offline reads and drafts; sensitive decisions stay online.
- Android FCM delivery, native sharing, files and notification deep links.

## Release readiness changes

- Version advanced to `1.0.0+2`.
- Android release builds now require a private upload keystore and cannot silently use
  debug signing.
- A separate Flutter Web staging Docker service is available; it cannot replace the
  existing PWA unless an operator deliberately changes Cloudflare routing.
- Release, privacy, support and pilot-feedback procedures are documented.

## Known controlled-pilot difference

Permanent member deletion remains available in the PWA for authorised roles and is not
yet exposed by the Flutter client. This is intentional for the first pilot; it does not
expand access and the PWA remains the fallback for that operation.
