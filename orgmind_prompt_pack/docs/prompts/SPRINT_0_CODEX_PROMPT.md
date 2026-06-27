# Sprint 0 Codex Prompt

You are implementing Sprint 0 for OrgMind AI.

Read first:
- 00_MASTER_PROMPT_CODEX.md
- 01_PROJECT_CONSTITUTION.md
- 02_ARCHITECTURE.md
- 03_ROADMAP_SPRINTS.md

Task:
Create the initial repository skeleton and runnable foundation.

Expected files:
- README.md
- .env.example
- docker-compose.yml
- apps/web Vue 3 skeleton
- services/api FastAPI skeleton
- docs folders
- infra folders
- .github/copilot-instructions.md
- .github/workflows/ci.yml

Rules:
- do not implement auth yet
- do not implement RAG yet
- no COMBIS hardcoding
- keep code and identifiers in English
- use Docker Compose as runtime

Acceptance criteria:
- `docker compose up --build` starts the baseline
- API exposes `/health`
- frontend opens
- README explains setup
