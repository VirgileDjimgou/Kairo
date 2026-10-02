---
applyTo: "apps/flutter_kairo/**/*.dart,apps/flutter_kairo/**/*.yaml,apps/flutter_kairo/**/*.yml"
---

# Kairo Flutter Instructions

**FROZEN / LEGACY REFERENCE (ADR-014).** The Vue 3 PWA is the canonical client.
Do not add new Flutter business features. This instruction applies only when
inspecting or, under an explicit separate decision, minimally maintaining the
frozen reference source.

Read `apps/flutter_kairo/AGENTS.md`, `docs/pwa/FLUTTER_TO_PWA_PARITY.md`,
`docs/flutter/PROJECT_STATUS.md`, `docs/flutter/FLUTTER_APP_ROADMAP.md`, and
`docs/flutter/FEATURE_PARITY.md` before touching Flutter files.

- The Vue PWA is the canonical client. Do not rewrite, remove or weaken it.
- FastAPI owns authorization, role resolution, tenant isolation, validation, audit, and
  finance/discipline decisions. Flutter must not duplicate or bypass those rules.
- Scope local data and offline commands by user and tenant. Clear them on sign-out,
  tenant switch, access recovery, or session revocation.
- Do not persist passwords or secrets. Use platform secure storage for session material.
- Provide French, English and German copy in any reference UI.
- Flutter checks run only through the manual `flutter-legacy` workflow; they never
  block the default release pipeline.
