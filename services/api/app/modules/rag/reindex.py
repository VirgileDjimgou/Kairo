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
    current = settings.ollama_embedding_model
    previous: str | None = None

    try:
        if os.path.isfile(sentinel_path):
            with open(sentinel_path) as f:
                data = json.load(f)
                previous = data.get("model")
    except (json.JSONDecodeError, OSError):
        pass

    changed = previous is not None and previous != current
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
        json.dump({"model": settings.ollama_embedding_model}, f)
    logger.info("embedding_model_persisted", model=settings.ollama_embedding_model)
