# VS Code, GitHub Copilot and Codex Setup

## 1. Recommended VS Code Extensions

Install:

- Python
- Pylance
- Ruff
- Mypy Type Checker
- Vue - Official
- TypeScript Vue Plugin if needed
- ESLint
- Prettier
- Docker
- GitHub Copilot
- GitHub Copilot Chat
- REST Client
- YAML
- Markdown All in One

---

## 2. Workspace File

Create `orgmind-ai.code-workspace`.

```json
{
  "folders": [
    { "path": "." },
    { "path": "apps/web" },
    { "path": "services/api" }
  ],
  "settings": {
    "editor.formatOnSave": true,
    "files.trimTrailingWhitespace": true,
    "python.defaultInterpreterPath": "services/api/.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["services/api/tests"],
    "typescript.preferences.importModuleSpecifier": "relative",
    "eslint.validate": ["javascript", "typescript", "vue"],
    "github.copilot.chat.codeGeneration.instructions": [
      {
        "text": "Follow the OrgMind AI constitution and architecture documents. Preserve tenant isolation, RBAC, provider abstractions, and source-grounded AI answers."
      }
    ]
  }
}
```

---

## 3. Copilot Instructions

Create `.github/copilot-instructions.md`.

```md
# GitHub Copilot Instructions for OrgMind AI

OrgMind AI is a local-first, multi-tenant RAG platform for organizations.

Always follow:
- 00_MASTER_PROMPT_CODEX.md
- 01_PROJECT_CONSTITUTION.md
- 02_ARCHITECTURE.md
- 03_ROADMAP_SPRINTS.md

Hard rules:
- never hardcode COMBIS as product logic
- tenant_id is mandatory for tenant-scoped data
- backend enforces permissions
- LLM never decides access control
- retrieval filters must run before prompt assembly
- no unauthorized chunks sent to LLM
- frontend never talks directly to PostgreSQL, Qdrant, MinIO, Redis, or Ollama
- use DTOs at API boundaries
- update tests and docs when behavior changes
- keep UI elegant, Bootstrap-based, and professional

Preferred stack:
- FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Vue 3, TypeScript, Pinia, Bootstrap 5
- Qdrant, MinIO, Redis, Ollama
- Docker Compose and Cloudflare Tunnel
```

---

## 4. Local Development Commands

```bash
# Start infra and apps
cp .env.example .env
docker compose up --build

# Start with Cloudflare tunnel profile
docker compose --profile tunnel up --build

# API tests
cd services/api
pytest

# Frontend dev
cd apps/web
npm run dev

# Frontend build
cd apps/web
npm run build
```

---

## 5. Codex Desktop Usage Strategy

Recommended workflow:

1. Open repository in Codex Desktop.
2. Ask Codex to read the constitution and sprint file.
3. Give one sprint task at a time.
4. Review diff.
5. Run tests.
6. Fix errors with targeted prompts.
7. Update docs.
8. Commit.

Do not ask for broad, vague changes.

---

## 6. Commit Message Style

Use:

```text
feat(auth): add tenant-scoped JWT login
feat(documents): add MinIO upload provider
feat(rag): add permission-aware retrieval
fix(security): enforce tenant filter on document list
chore(infra): add Cloudflare Tunnel profile
```
