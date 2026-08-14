# Sprint F0 Validation Evidence

Date: 2026-08-07

## Automated checks

| Check | Result |
| --- | --- |
| `flutter analyze` | Passed — no issues |
| `flutter test` | Passed — 5 tests |
| `flutter build web` production configuration | Passed |
| `flutter build apk --debug` | Passed |

## Visual checks

| Target | Viewport | Result |
| --- | --- | --- |
| Flutter Web mobile simulation | 390 × 844 | Passed — compact header, stacked cards, bottom navigation and no text overflow |
| Flutter Web desktop simulation | 1280 × 900 | Passed — navigation rail, two-card layout and readable top bar |

## Configuration used for Web validation

```text
KAIRO_FLAVOR=production
KAIRO_API_BASE_URL=https://app.combissportverein.org/api/v1
```

No credentials, tokens, or production secrets are embedded in the client.
