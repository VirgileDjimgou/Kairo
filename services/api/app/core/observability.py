from __future__ import annotations

from time import monotonic
from uuid import uuid4

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.metrics import metrics, normalize_error_code

logger = structlog.get_logger(__name__)


def _request_id(request: Request) -> str:
    incoming = request.headers.get("X-Request-ID", "").strip()
    return incoming or uuid4().hex


def _error_payload(*, request_id: str, error_code: str, detail: object) -> dict:
    return {
        "detail": detail,
        "error_code": error_code,
        "request_id": request_id,
    }


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = _request_id(request)
        request.state.request_id = request_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            http_method=request.method,
            http_path=request.url.path,
        )

        start = monotonic()
        try:
            response = await call_next(request)
        finally:
            elapsed_ms = int((monotonic() - start) * 1000)
            structlog.contextvars.clear_contextvars()

        response.headers["X-Request-ID"] = request_id
        metrics.record_http_request(request.method, response.status_code, elapsed_ms)
        return response


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    request_id = getattr(request.state, "request_id", uuid4().hex)
    error_code = normalize_error_code(exc.status_code, exc.detail)
    metrics.record_error(error_code)
    headers = dict(exc.headers or {})
    headers["X-Request-ID"] = request_id
    headers["X-Error-Code"] = error_code
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(
            request_id=request_id,
            error_code=error_code,
            detail=exc.detail,
        ),
        headers=headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", uuid4().hex)
    error_code = "validation_error"
    metrics.record_error(error_code)
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            request_id=request_id,
            error_code=error_code,
            detail=exc.errors(),
        ),
        headers={
            "X-Request-ID": request_id,
            "X-Error-Code": error_code,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", uuid4().hex)
    error_code = "internal_error"
    metrics.record_error(error_code)
    logger.exception("unhandled_exception", request_id=request_id, error=str(exc))
    return JSONResponse(
        status_code=500,
        content=_error_payload(
            request_id=request_id,
            error_code=error_code,
            detail="Internal server error",
        ),
        headers={
            "X-Request-ID": request_id,
            "X-Error-Code": error_code,
        },
    )
