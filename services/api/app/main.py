from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app._version import __version__
from app.core.config import settings
from app.core.dependencies import DbDep
from app.core.metrics import build_runtime_metrics
from app.db.session import async_session_factory
from app.modules.rag.reindex import check_embedding_model_changed, persist_embedding_model
from app.core.observability import (
    ObservabilityMiddleware,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.health_checks import run_all_checks
from app.core.logging import setup_logging
from app.modules.tenancy.module_toggles import ALL_MODULES
from app.modules.chat.router import router as chat_router
from app.modules.audit.router import router as audit_router
from app.modules.admin.router import router as admin_router
from app.modules.documents.router import router as documents_router
from app.modules.identity.router import router as identity_router
from app.modules.tenancy.router import router as tenancy_router
from app.modules.membership.router import router as membership_router
from app.modules.contributions.router import router as contributions_router
from app.modules.policies.router import router as policies_router
from app.modules.disciplinary.router import router as disciplinary_router
from app.modules.events.router import router as events_router
from app.modules.events.sports_router import router as sports_router
from app.modules.announcements.router import router as announcements_router
from app.modules.notifications.router import callback_router as notifications_callback_router
from app.modules.notifications.router import router as notifications_router

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
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ── API v1 routers ─────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(identity_router, prefix=API_PREFIX)
app.include_router(tenancy_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(audit_router, prefix=API_PREFIX)
app.include_router(documents_router, prefix=API_PREFIX)
app.include_router(chat_router, prefix=API_PREFIX)
app.include_router(membership_router, prefix=API_PREFIX)
app.include_router(contributions_router, prefix=API_PREFIX)
app.include_router(policies_router, prefix=API_PREFIX)
app.include_router(disciplinary_router, prefix=API_PREFIX)
app.include_router(events_router, prefix=API_PREFIX)
app.include_router(sports_router, prefix=API_PREFIX)
app.include_router(announcements_router, prefix=API_PREFIX)
app.include_router(notifications_router, prefix=API_PREFIX)
app.include_router(notifications_callback_router, prefix=API_PREFIX)


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

    statuses = [c["status"] for c in checks.values()]
    if all(s == "ok" for s in statuses):
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


@app.get("/metrics", tags=["system"], summary="Runtime metrics")
async def metrics(db: DbDep) -> PlainTextResponse:
    return PlainTextResponse(await build_runtime_metrics(db), media_type="text/plain; version=0.0.4")
