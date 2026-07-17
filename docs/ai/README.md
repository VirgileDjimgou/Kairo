# AI Continuity Hub

This folder is the continuity hub for agentic IDE sessions on Kairo.

## Authoritative Files

- `PROJECT_STATE.md`: verified implementation snapshot
- `NEXT_SPRINT.md`: immediate execution target
- `POST_AUDIT_ROADMAP_2026-07-17.md`: dense roadmap extension after the July 17, 2026 audit pass
- `AUDIT_WEAKNESSES_2026-07-17.md`: evidence-backed weakness summary used to build the post-audit roadmap

## Prompt Files

- `prompts/KAIRO_CONTINUE_UNIVERSAL.md`: full execution prompt and current canonical universal prompt
- `prompts/KAIRO_UNIVERSAL_COMPACT.md`: compact operator-grade continuation prompt
- `PROMPT_SESSION_HANDOFF_TEMPLATE.md`: reusable handoff prompt when a session stops mid-task

## Compatibility Files

- `PROMPT_UNIVERSAL_NEXT_SPRINT.md`: deprecated compatibility pointer kept to avoid breaking older references

## Recommended Read Order

At the start of a new session, read:

1. `README.md`
2. `AGENTS.md`
3. `constitution/KAIRO_CONSTITUTION.md`
4. `IMPLEMENTATION_ROADMAP.md`
5. `PROJECT_STATUS.md`
6. `docs/ai/PROJECT_STATE.md`
7. `docs/ai/NEXT_SPRINT.md`
8. `prompts/CODEX_AUTOPILOT.md`
9. `prompts/KAIRO_CONTINUE_UNIVERSAL.md`

## Usage

- Use `NEXT_SPRINT.md` when the goal is direct execution of the active roadmap sprint.
- Use `POST_AUDIT_ROADMAP_2026-07-17.md` when planning the next dense delivery cycle after Sprint 85.
- Use `AUDIT_WEAKNESSES_2026-07-17.md` when you need the audit evidence behind roadmap prioritization.
