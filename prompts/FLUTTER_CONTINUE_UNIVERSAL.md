# Flutter Continuation Prompt

**CLOSED — the Flutter client is FROZEN as legacy/reference code during the active
Roadmap V2 program S119–S128 (ADR-014). Do not use the command below to start new
Flutter business work.** The Vue 3 PWA (`apps/web/`) is the canonical client;
capability continuity is tracked in `docs/pwa/FLUTTER_TO_PWA_PARITY.md`.

The instruction below is retained as the historical record of the former Flutter
track:

```text
Continue Next Sprint Implementation Flutter App
```

It means:

```text
You are continuing the parallel Kairo Flutter client. Do not modify or replace the
production Vue 3 PWA unless the task explicitly requires a shared API contract change.

Before writing code, read:
1. README.md
2. AGENTS.md
3. apps/flutter_kairo/AGENTS.md
4. docs/flutter/PROJECT_STATUS.md
5. docs/flutter/FLUTTER_APP_ROADMAP.md
6. docs/flutter/FEATURE_PARITY.md
7. the relevant Vue 3 screen and FastAPI API contract

Inspect git status and determine the single active or first unfinished Flutter sprint.
Implement only that sprint. Do not skip ahead.

Treat FastAPI as the sole source of truth for tenant isolation, roles, finance,
discipline, audit, session revocation and business validation. Never store passwords.
Scope local cache and queued offline work by tenant and authenticated user. Never finalise
financial, disciplinary, role, deletion or restore operations offline.

For every completed capability, compare the existing PWA's functional, responsive and
role behaviour. Update FEATURE_PARITY.md with evidence, run the relevant Dart tests,
Android build and Flutter Web build, then update PROJECT_STATUS.md and the roadmap.

Finish with: sprint executed, role coverage, parity rows updated, files changed, tests
and builds run, visual evidence, remaining risks, and the next Flutter sprint.
```
