# Flutter F8 Android Notification Activation

## Delivered client foundations

- Every authenticated installation receives a random identifier held in platform
  secure storage; it is registered with the existing authenticated
  `POST /notifications/devices` API and is never an account identifier.
- Android 13 notification permission is declared. The product must request it
  only after an explicit member action and must retain normal in-app inbox access
  when it is denied.
- Notification taps already use FastAPI-owned target paths in the inbox; the
  authenticated shell dispatches the target and FastAPI still applies route and
  data permissions.
- Finance reports invoke the native Android share sheet. Document-authorised
  officers can select a file and upload it through the existing API contract.

## Firebase Cloud Messaging implementation

- The Android Firebase client configuration is present locally and excluded from
  source control. The Flutter package identifier must remain aligned with it.
- A user enables Android notifications explicitly from the Notifications screen;
  only then does the app request Android permission, obtain an FCM token and submit
  it to `POST /notifications/mobile-push-tokens`.
- The client cancels its authenticated FCM token-refresh callback on sign-out or
  session revocation. A later opt-in creates a new callback under the current
  authenticated tenant/user session.
- The FastAPI contract creates a device/profile using the authenticated tenant and
  user, then persists the opaque FCM token in a tenant-isolated table. The same
  Android device can therefore be used with separate association accounts without
  mixing their delivery registrations.
- The outbox sends generic lock-screen text only. Business content stays behind the
  authenticated inbox and FastAPI permission checks.

## Production server activation

`google-services.json` configures the Android client only. To deliver push, download
the distinct Firebase Admin service-account JSON from Firebase Console and store it
outside source control at `services/api/.private/firebase-admin.json`. Then set the
following values in the protected `.env.core` file:

```dotenv
FIREBASE_MESSAGING_ENABLED=true
FIREBASE_SERVICE_ACCOUNT_PATH=/run/secrets/kairo/firebase-admin.json
```

The core API container mounts this private directory read-only. Do not place the
Admin JSON in the Flutter project, browser bundle or Git repository.

The API and the asynchronous notification worker both mount this directory read-only,
because the worker is responsible for outbox delivery.

## Executed Android validation

- The production-configured APK was installed on an Android 15 Google Play emulator.
- Explicit notification permission and the enabled state were captured.
- The authenticated installation registered its FCM token through FastAPI.
- A server outbox event was processed while Kairo was in the background. Android
  displayed the generic notification `Une nouvelle notification est disponible.`
- Tapping it reopened Kairo and dispatched the authorised `/finance` target.
- Real API login and role-aware dashboards were exercised for secretary general,
  auditor, censor, sports manager, vice president, administrator and treasurer.
- The final host run exposed only the emulator through ADB. The earlier Samsung launch
  proof is retained separately, but it is not claimed as background-delivery evidence.

Evidence is indexed by `apps/flutter_kairo/artifacts/sprint-f8/README.md`.

## Threat-model decision

The app already stores only the access token in platform secure storage. Biometric or
PIN re-entry is deferred until F9: it needs physical-device lifecycle validation and
must not lock users out of a shared association device. FastAPI sessions, sign-out and
session revocation remain the immediate controls.
