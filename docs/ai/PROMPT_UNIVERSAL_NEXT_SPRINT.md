# Universal Prompt For The Next Sprint

Paste the prompt below into Codex, Cursor, or GitHub Copilot Chat.

```text
You are continuing work on Kairo (OrgMind AI).

Before making changes, read these files in order:
- README.md
- AGENTS.md
- docs/ai/PROJECT_STATE.md
- docs/ai/NEXT_SPRINT.md
- orgmind_prompt_pack/01_PROJECT_CONSTITUTION.md
- orgmind_prompt_pack/02_ARCHITECTURE.md
- orgmind_prompt_pack/03_ROADMAP_SPRINTS.md
- orgmind_prompt_pack/09_SECURITY_AND_LLM_SAFETY.md

Then inspect the current codebase and continue with the official next sprint only:
- Sprint 6 - First RAG Chat

Implementation goals:
- add backend `rag` and `chat` modules
- add the first permission-aware retrieval flow
- add LLM generation through a provider abstraction
- expose the first chat query endpoint
- return citations with grounded answers
- refuse answers when no reliable source is found
- add the first frontend chat view if the backend slice is ready

Hard rules:
- preserve tenant isolation everywhere
- backend is the only policy enforcement point
- never let the LLM decide permissions
- never send unauthorized chunks to the LLM
- do not implement later roadmap sprints
- keep changes small and explicit
- add or update tests
- update docs/ai/PROJECT_STATE.md and docs/ai/NEXT_SPRINT.md if sprint status changes

If you find blocking inconsistencies from earlier work, fix only the minimum needed to complete Sprint 6 safely, then proceed.

At the end:
- summarize what was implemented
- list any remaining blockers
- mention which tests were run
```
