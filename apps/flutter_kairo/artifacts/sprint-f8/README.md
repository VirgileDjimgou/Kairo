# Sprint F8 Android Evidence

All images were produced by automated ADB or Flutter golden tests. The final runtime
used the production API endpoint through Cloudflare.

## Runtime and roles

- `emulator-secretary-dashboard.png` — secretary general, compact five-item navigation;
- `emulator-auditor-dashboard.png` — auditor role dashboard;
- `emulator-censor-dashboard.png` — censor role dashboard;
- `emulator-sports-dashboard.png` — sports manager role dashboard;
- `emulator-vice-president-dashboard.png` — vice-president role dashboard;
- `emulator-admin-dashboard.png` — administrator role dashboard;
- `emulator-treasurer-navigation.png` — treasurer responsive navigation;
- `emulator-treasurer-dashboard.png` — real treasury workspace data.
- `emulator-login-network-error.png` — a forced network loss ends with an explicit
  recoverable error instead of an indefinite white loading screen.

Each runtime PNG has a matching UI Automator XML file where assertions needed semantic
role, route or navigation evidence.

## Notifications

- `emulator-notification-permission.png` — Android runtime permission request;
- `emulator-notification-enabled.png` — registered/enabled notification state;
- `emulator-push-background.png` — FCM notification shown while Kairo is backgrounded;
- `emulator-push-deep-link.png` — notification tap opened the authorised finance route;
- `emulator-inbox-before-push.png` — authenticated in-app inbox before background proof.
- `physical-device/samsung-notification-permission.png` — Android notification activation
  confirmed on the connected Samsung SM-G975F;
- `physical-device/samsung-push-background.png` — real FCM notification received in the
  Samsung system tray while Kairo was backgrounded;
- `physical-device/samsung-push-deep-link.png` — tapping that notification returns to
  the authorised authenticated notification route.

## Generated feature proofs

- `android-notification-activation.png` — notification activation surface;
- `android-secretary-document-import.png` — authorised native document selection/import.

The final host run included both the Google Play emulator and a Samsung SM-G975F over
USB. The physical-device folder contains the install, sign-in, responsive navigation,
notification opt-in, background delivery and deep-link evidence.
