# Sprint F9 Release-Readiness Evidence

- `sign-in-android.png` is the regression baseline at 390 × 844.
- `sign-in-web.png` is the regression baseline at 1280 × 900.
- `sprint_f9_release_readiness_test.dart` verifies the French sign-in control,
  password-visibility action and semantic labels at both widths.
- Physical Android notification and authenticated deep-link proof remains in
  `../sprint-f8/physical-device/`; F9 does not replace those device capabilities.

The text blocks in Flutter golden images are expected font-test rendering. Functional
text, accessibility semantics and responsive structure are asserted by the widget test;
real-device screenshots remain the source for platform-font visual review.
