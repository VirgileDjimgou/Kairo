from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app._version import __version__
from app.core.config import settings
from app.core.dependencies import DbDep
from app.core.health_checks import run_all_checks, run_readiness_checks
from app.core.logging import setup_logging
from app.core.metrics import build_runtime_metrics
from app.core.observability import (
    ObservabilityMiddleware,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.db.session import async_session_factory
from app.modules.module_registry.descriptor import default_registry
from app.modules.rag.reindex import check_embedding_model_changed, persist_embedding_model
from app.modules.tenancy.module_toggles import ALL_MODULES

setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    logger.info("Starting Kairo API", env=settings.app_env, version=__version__)

    if settings.indexing_auto_enabled:
        changed = check_embedding_model_changed()
        if changed:
            logger.warning("embedding_model_changed_triggering_reindex")
            from app.modules.documents.repository import DocumentRepository

            async with async_session_factory() as session:
                repo = DocumentRepository(session)
                await repo.flag_all_documents_for_reindex()
            logger.info("reindex_triggered_all_documents")
        persist_embedding_model()

    yield
    logger.info("Kairo API shutdown complete")


app = FastAPI(
    title="Kairo — OrgMind AI API",
    version=__version__,
    description=(
        "Local-first multi-tenant RAG platform for organizations. "
        "Backend is the sole policy enforcement point."
    ),
    lifespan=lifespan,
    # Disable docs in production to avoid exposing API surface
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
)

app.add_middleware(ObservabilityMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)

# ── API v1 routers ─────────────────────────────────────────────────────────────
# Routers are composed from the internal Module Registry (descriptor order), so a
# new module is registered by adding one package with a ``module.py`` descriptor.
API_PREFIX = "/api/v1"

for module_router, _router_attr in default_registry().routers():
    app.include_router(module_router, prefix=API_PREFIX)


# ── System endpoints ───────────────────────────────────────────────────────────

@app.get("/health", tags=["system"], summary="Health check")
async def health_check(db: DbDep) -> dict:
    """
    Probes critical dependencies and returns their status.

    Returns HTTP 200 in all cases — callers should inspect the `status`
    field (`ok` | `degraded` | `unavailable`) and per-service `checks`
    to determine overall health.
    """
    checks = await run_all_checks(db)

    statuses = [c["status"] for c in checks.values()]  # type: ignore[index]
    # Optional services explicitly disabled by the deployment profile are not
    # failures. This lets the Web/PWA core report healthy without an AI runtime.
    active_statuses = [status for status in statuses if status != "disabled"]
    if all(s == "ok" for s in active_statuses):
        overall = "ok"
    elif any(s == "unavailable" for s in statuses):
        overall = "unavailable"
    else:
        overall = "degraded"

    return {
        "status": overall,
        "version": __version__,
        "env": settings.app_env,
        "checks": checks,
        "modules": ALL_MODULES,
    }


@app.get("/health/live", tags=["system"], summary="Liveness probe")
async def liveness_check() -> dict:
    """Process liveness: always 200 while the API can answer requests."""
    return {"status": "ok", "version": __version__}


@app.get("/health/ready", tags=["system"], summary="Readiness probe")
async def readiness_check(db: DbDep) -> JSONResponse:
    """Readiness gates on critical dependencies only (database, Redis)."""
    checks = await run_readiness_checks(db)
    ready = all(
        check["status"] in {"ok", "disabled"}  # type: ignore[index]
        for check in checks.values()
    )
    return JSONResponse(
        status_code=200 if ready else 503,
        content={
            "status": "ready" if ready else "not_ready",
            "version": __version__,
            "checks": checks,
        },
    )


@app.get("/metrics", tags=["system"], summary="Runtime metrics")
async def metrics(db: DbDep) -> PlainTextResponse:
    return PlainTextResponse(await build_runtime_metrics(db), media_type="text/plain; version=0.0.4")
