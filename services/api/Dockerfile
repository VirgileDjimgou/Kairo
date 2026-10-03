# ── Stage 1: dependency builder ────────────────────────────────────────────────
FROM python:3.12-slim@sha256:dddfd7e07f9d15aeeca61529320492139d21cac7f0070c00609243e51e4e0016 AS builder

WORKDIR /build

# System deps for psycopg async and bcrypt compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt is the direct dependency contract; requirements.lock pins
# every resolved version for reproducible production builds.
COPY requirements.txt requirements.lock ./
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt -c requirements.lock

# ── Stage 2: development (with hot-reload) ────────────────────────────────────
FROM python:3.12-slim@sha256:dddfd7e07f9d15aeeca61529320492139d21cac7f0070c00609243e51e4e0016 AS development

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 8000

# --proxy-headers lets the API trust X-Forwarded-Proto from the reverse proxy so
# generated redirects and absolute URLs keep the public HTTPS scheme.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers --forwarded-allow-ips='*'"]

# ── Stage 3: production ───────────────────────────────────────────────────────
FROM python:3.12-slim@sha256:dddfd7e07f9d15aeeca61529320492139d21cac7f0070c00609243e51e4e0016 AS production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 8000

# Database migrations are an explicit release step. Keeping them out of the
# long-running process prevents concurrent migration attempts during restarts.
#
# --proxy-headers makes the API honour X-Forwarded-Proto from the reverse proxy.
# Without it, FastAPI builds absolute redirect URLs from the internal HTTP
# scheme and an HTTPS browser blocks them as mixed content.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
