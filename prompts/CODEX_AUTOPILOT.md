# Codex Autopilot Prompt

Use this prompt at the beginning of a new Codex, Cursor, or GitHub Copilot session:

```text
Continue Kairo.

Read:
- constitution/KAIRO_CONSTITUTION.md
- IMPLEMENTATION_ROADMAP.md
- PROJECT_STATUS.md
- prompts/Master_Prompt_Codex.md

Determine the current sprint.
Implement only the current sprint or the next unfinished sprint.

Rules:
- Do not build the whole platform in one pass.
- Preserve tenant isolation and backend-first permission enforcement.
- Never let the LLM decide access control.
- Never send unauthorized chunks to the LLM.
- Keep changes small and explicit.
- Add or update tests for touched logic.
- Update documentation when architecture, contracts, security posture, or behavior changes.
- Update PROJECT_STATUS.md and IMPLEMENTATION_ROADMAP.md before stopping if sprint progress changed.
- If a build or test fails, analyze, fix, rerun, and continue within the same sprint.
- Stop when the sprint is complete and verified.
```

## Short Alias

```text
Continue Kairo.
```

The alias means: read the project memory, determine the current sprint, and continue only the current sprint or next unfinished sprint.
