from __future__ import annotations

import json
import os

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

_EMBEDDING_MODEL_SENTINEL_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", ".embedding_model"
)


def _get_sentinel_path() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", ".embedding_model")
    )


def check_embedding_model_changed() -> bool:
    """Return True if the embedding model changed since last run."""
    sentinel_path = _get_sentinel_path()
    current = _embedding_identity()
    previous: str | None = None
    previous_dimensions: int | None = None

    try:
        if os.path.isfile(sentinel_path):
            with open(sentinel_path) as f:
                data = json.load(f)
                previous = data.get("identity") or data.get("model")
                previous_dimensions = data.get("dimensions")
    except (json.JSONDecodeError, OSError):
        pass

    changed = previous is not None and (
        previous != current or previous_dimensions != settings.embedding_dimensions
    )
    if changed:
        logger.warning("embedding_model_changed", previous=previous, current=current)
    else:
        logger.info("embedding_model_unchanged", model=current)

    return changed


def persist_embedding_model() -> None:
    """Write the current embedding model to the sentinel file."""
    sentinel_path = _get_sentinel_path()
    os.makedirs(os.path.dirname(sentinel_path), exist_ok=True)
    with open(sentinel_path, "w") as f:
        json.dump(
            {
                "model": _embedding_identity(),
                "identity": _embedding_identity(),
                "dimensions": settings.embedding_dimensions,
                "provider": settings.embedding_provider_kind,
            },
            f,
        )
    logger.info(
        "embedding_model_persisted",
        model=_embedding_identity(),
        provider=settings.embedding_provider_kind,
    )


def _embedding_identity() -> str:
    if settings.embedding_provider_kind == "remote_ai_runtime":
        return settings.ai_embedding_profile or "remote-ai-runtime"
    if settings.embedding_provider_kind == "openai_compatible":
        return settings.openai_compatible_embedding_model
    return settings.ollama_embedding_model
