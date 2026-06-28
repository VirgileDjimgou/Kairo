# Session Handoff Prompt Template

Use this when a session stopped in the middle of a task and you want another IDE or agent to resume cleanly.

```text
You are resuming work on Kairo (OrgMind AI).

Read first:
- README.md
- AGENTS.md
- docs/ai/PROJECT_STATE.md
- docs/ai/NEXT_SPRINT.md
- orgmind_prompt_pack/01_PROJECT_CONSTITUTION.md
- orgmind_prompt_pack/02_ARCHITECTURE.md
- orgmind_prompt_pack/03_ROADMAP_SPRINTS.md
- orgmind_prompt_pack/09_SECURITY_AND_LLM_SAFETY.md

Then inspect the current repository state and continue the active task.

Session handoff:
- Active sprint or task: [fill this]
- Files already touched: [fill this]
- What is already working: [fill this]
- Remaining work: [fill this]
- Tests already run: [fill this]
- Known blockers or risks: [fill this]

Rules:
- preserve tenant isolation
- do not modify unrelated modules
- keep the current sprint scope tight
- update docs if behavior changes

At the end:
- state exactly what was completed
- state what still remains
- list the tests run
```
