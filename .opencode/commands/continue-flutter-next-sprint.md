---
description: Frozen — do not start new Flutter business work during S119-S128
---

Continue Next Sprint Implementation Flutter App.

STOP: the Flutter client is FROZEN as legacy/reference code during the active
Roadmap V2 program S119–S128. This command must not be used to start new Flutter
business features.

The Vue 3 PWA is the canonical client. Flutter source is preserved only so it can be
consulted for behavior, notification and parity reference. It receives no new
business features, is not a blocking job of the default release pipeline, and must
not replace, weaken or silently change the PWA.

If the operator explicitly needs Flutter reference information, read (do not modify
without an explicit, separate decision):

1. `apps/flutter_kairo/AGENTS.md`
2. `docs/flutter/PROJECT_STATUS.md`
3. `docs/flutter/FLUTTER_APP_ROADMAP.md`
4. `docs/flutter/FEATURE_PARITY.md`
5. `prompts/FLUTTER_CONTINUE_UNIVERSAL.md`

Any Flutter archival or deletion is a separate explicit decision after S128, never
part of these sprints.
