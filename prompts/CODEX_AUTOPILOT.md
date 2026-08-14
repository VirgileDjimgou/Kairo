# Codex Autopilot Prompt

This file is the short launcher for Kairo sessions.
For the complete portable handoff prompt, use:

- `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

Short alias:

```text
Continue Kairo.
```

Meaning: read the project memory, determine the current sprint or the next unfinished sprint, then continue autonomously within that sprint only.

## Flutter Parallel Client Alias

```text
Continue Next Sprint Implementation Flutter App
```

Meaning: read `apps/flutter_kairo/AGENTS.md`, `docs/flutter/PROJECT_STATUS.md`,
`docs/flutter/FLUTTER_APP_ROADMAP.md`, `docs/flutter/FEATURE_PARITY.md`, and
`prompts/FLUTTER_CONTINUE_UNIVERSAL.md`; then implement only the active or next
unfinished Flutter sprint without modifying the Vue 3 PWA.
