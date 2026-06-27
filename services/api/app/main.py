from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import async_session_factory
from app.modules.documents.router import router as documents_router
from app.modules.identity.router import router as identity_router
from app.modules.tenancy.router import router as tenancy_router

setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    logger.info("Starting Kairo API", env=settings.app_env, version="0.1.0")
    yield
    logger.info("Kairo API shutdown complete")


app = FastAPI(
    title="Kairo — OrgMind AI API",
    version="0.1.0",
    description=(
        "Local-first multi-tenant RAG platform for organizations. "
        "Backend is the sole policy enforcement point."
    ),
    lifespan=lifespan,
    # Disable docs in production to avoid exposing API surface
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API v1 routers ─────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(identity_router, prefix=API_PREFIX)
app.include_router(tenancy_router, prefix=API_PREFIX)
app.include_router(documents_router, prefix=API_PREFIX)


# ── System endpoints ───────────────────────────────────────────────────────────

@app.get("/health", tags=["system"], summary="Health check")
async def health_check() -> dict:
    """
    Probes critical dependencies and returns their status.

    Returns HTTP 200 in all cases — callers should inspect the `status`
    field (`ok` | `degraded`) to determine overall health.
    """
    checks: dict[str, str] = {}

    # Database probe
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.warning("Database health check failed", error=str(exc))
        checks["database"] = "error"

    # Future sprints: Redis, Qdrant, MinIO probes added here

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "version": "0.1.0",
        "env": settings.app_env,
        "checks": checks,
    }
