# Flutter Privacy And Support Procedure

## Data handled by the client

The Flutter client accesses association data only through the authenticated Kairo API:
account identity, tenant membership, authorised member, finance, governance and
disciplinary data, and opted-in notification preferences. Passwords are entered only
for API authentication and are never stored by the client.

Android may store an access-session secret using platform secure storage and may send
an FCM registration token to the API after the user enables notifications. Notification
payloads are deliberately generic and do not expose confidential finance or discipline
details on a lock screen.

## User controls

- Sign out clears the authenticated client session and identity-scoped offline cache.
- Notifications can be enabled or disabled in the app and at operating-system level.
- Password recovery and role access remain controlled by the authorised FastAPI flow.
- Questions about personal data or account access are handled by the association's
  designated officers through the existing governance process.

## Support triage

For a report, collect the app version, platform, role, non-sensitive time window,
screen/route, reproducible steps, expected and actual result. Never request a password,
MFA code, access token, keystore, Firebase service-account file or full confidential
record in a support message.

Classify sign-in failures, cross-role visibility, unexpected finance mutations,
discipline exposure and backup/restore issues as urgent. Preserve audit records and
server data while investigating. For a client-only outage, direct users to the stable
PWA without altering the association data.
