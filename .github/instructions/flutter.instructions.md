---
applyTo: "apps/flutter_kairo/**/*.dart,apps/flutter_kairo/**/*.yaml,apps/flutter_kairo/**/*.yml"
---

# Kairo Flutter Instructions

Read `apps/flutter_kairo/AGENTS.md`, `docs/flutter/PROJECT_STATUS.md`,
`docs/flutter/FLUTTER_APP_ROADMAP.md`, and `docs/flutter/FEATURE_PARITY.md` before
editing Flutter files.

- The Vue PWA is a separate production client. Do not rewrite or remove it.
- Implement only the active Flutter sprint and update the parity matrix with proof.
- FastAPI owns authorization, role resolution, tenant isolation, validation, audit, and
  finance/discipline decisions. Flutter must not duplicate or bypass those rules.
- Scope local data and offline commands by user and tenant. Clear them on sign-out,
  tenant switch, access recovery, or session revocation.
- Do not persist passwords or secrets. Use platform secure storage for session material.
- Provide French, English and German copy from the first Flutter screen.
- Test Android and Flutter Web for each finished vertical slice; include loading, empty,
  error, offline and keyboard/accessibility states where applicable.
