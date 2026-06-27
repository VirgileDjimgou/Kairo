# Configuration Guide

This document defines the configuration files that Codex or GitHub Copilot should generate progressively.

---

## 1. Environment Variables

Create `.env.example` at the repository root.

```env
# Project
APP_NAME=OrgMind AI
APP_ENV=development
APP_DEBUG=true
APP_BASE_URL=http://localhost:5173
API_BASE_URL=http://localhost:8000

# Security
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
POSTGRES_DB=orgmind
POSTGRES_USER=orgmind
POSTGRES_PASSWORD=orgmind_dev_password
DATABASE_URL=postgresql+psycopg://orgmind:orgmind_dev_password@postgres:5432/orgmind

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO
MINIO_ROOT_USER=orgmind
MINIO_ROOT_PASSWORD=orgmind_dev_password
MINIO_ENDPOINT=minio:9000
MINIO_PUBLIC_ENDPOINT=http://localhost:9000
MINIO_BUCKET_DOCUMENTS=documents

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=orgmind_document_chunks

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_LLM_MODEL=qwen2.5:7b-instruct
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=OrgMind AI

# Upload limits
MAX_UPLOAD_MB=50
ALLOWED_UPLOAD_EXTENSIONS=pdf,docx,txt,md,csv,png,jpg,jpeg,webp

# Cloudflare
CLOUDFLARE_TUNNEL_TOKEN=
```

---

## 2. Docker Compose Baseline

Create `docker-compose.yml`.

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  api:
    build:
      context: ./services/api
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
      qdrant:
        condition: service_started
      minio:
        condition: service_started
      ollama:
        condition: service_started
    volumes:
      - ./services/api:/app

  worker:
    build:
      context: ./services/api
    command: celery -A app.worker.celery_app worker --loglevel=info
    env_file:
      - .env
    depends_on:
      - api
      - redis
    volumes:
      - ./services/api:/app

  web:
    build:
      context: ./apps/web
    env_file:
      - .env
    ports:
      - "5173:5173"
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    depends_on:
      - api

  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}
    env_file:
      - .env
    depends_on:
      - web
      - api
    profiles:
      - tunnel

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  minio_data:
  ollama_data:
```

---

## 3. Cloudflare Tunnel Local Config Alternative

Create `infra/cloudflare/config.yml`.

```yaml
tunnel: orgmind-ai-local
credentials-file: /home/USER/.cloudflared/orgmind-ai-local.json

ingress:
  - hostname: orgmind.example.com
    service: http://localhost:5173
  - hostname: api.orgmind.example.com
    service: http://localhost:8000
  - service: http_status:404
```

For one-domain routing, place the API behind a reverse proxy later.

---

## 4. Frontend Bootstrap Setup

Install:

```bash
npm install bootstrap bootstrap-icons pinia vue-router axios
npm install -D sass
```

In `src/main.ts`:

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap'
import './styles/main.scss'

createApp(App).use(createPinia()).use(router).mount('#app')
```

---

## 5. Backend Dependencies

Create `services/api/requirements.txt`.

```txt
fastapi
uvicorn[standard]
pydantic
pydantic-settings
sqlalchemy
psycopg[binary]
alembic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
redis
celery
qdrant-client
boto3
pymupdf
python-docx
pillow
pytesseract
httpx
structlog
pytest
pytest-asyncio
ruff
mypy
```

---

## 6. GitHub Actions CI

Create `.github/workflows/ci.yml`.

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install API dependencies
        run: |
          cd services/api
          pip install -r requirements.txt
      - name: Lint API
        run: |
          cd services/api
          ruff check app tests
      - name: Test API
        run: |
          cd services/api
          pytest

  web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install Web dependencies
        run: |
          cd apps/web
          npm ci
      - name: Build Web
        run: |
          cd apps/web
          npm run build
```
