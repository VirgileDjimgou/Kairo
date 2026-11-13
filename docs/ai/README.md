# AI Continuity Hub

This folder is the continuity hub for agentic IDE sessions on Kairo.

## Authoritative Files

- `SESSION_BRIEF.md`: generated one-page session warm-up (do not edit by hand;
  regenerate with `npm run session:brief -- --write`)
- `PROJECT_STATE.md`: verified implementation snapshot
- `NEXT_SPRINT.md`: how the next sprint is resolved (no status is tracked there)
- `POST_AUDIT_ROADMAP_2026-07-17.md`: dense roadmap extension after the July 17, 2026 audit pass
- `AUDIT_WEAKNESSES_2026-07-17.md`: evidence-backed weakness summary used to build the post-audit roadmap

## Prompt Files

- `prompts/KAIRO_CONTINUE_UNIVERSAL.md`: full execution prompt and current canonical universal prompt
- `prompts/KAIRO_UNIVERSAL_COMPACT.md`: compact operator-grade continuation prompt
- `PROMPT_SESSION_HANDOFF_TEMPLATE.md`: reusable handoff prompt when a session stops mid-task

## Compatibility Files

- `PROMPT_UNIVERSAL_NEXT_SPRINT.md`: deprecated compatibility pointer kept to avoid breaking older references

## Recommended Read Order

At the start of a new session, run `npm run session:brief` (or read
`SESSION_BRIEF.md`). Then read only the documents the task routing table names.

Do not read `IMPLEMENTATION_ROADMAP.md`, `PROJECT_STATUS.md`,
`orgmind_prompt_pack/` or the Flutter documents in full to "get oriented"; they are
reference material for a specific task, not a warm-up.

## Usage

- Use `NEXT_SPRINT.md` when the goal is direct execution of the active roadmap sprint.
- Use `POST_AUDIT_ROADMAP_2026-07-17.md` when planning the next dense delivery cycle after Sprint 85.
- Use `AUDIT_WEAKNESSES_2026-07-17.md` when you need the audit evidence behind roadmap prioritization.
