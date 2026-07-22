from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class SentenceTransformersReranker:
    """Cross-encoder reranker using sentence-transformers (optional dependency)."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or "cross-encoder/ms-marco-MiniLM-L-12-v2"
        self._model = None
        self._available = False
        self._load_error: str | None = None

    def _init_model(self) -> None:
        if self._model is not None or self._load_error:
            return
        try:
            from sentence_transformers import CrossEncoder

            logger.info("loading_cross_encoder", model=self._model_name)
            self._model = CrossEncoder(self._model_name)
            self._available = True
        except ImportError:
            self._load_error = "sentence-transformers not installed"
            logger.warning("reranker_unavailable", reason=self._load_error)
        except Exception as exc:
            self._load_error = str(exc)
            logger.warning("reranker_load_failed", error=str(exc))

    def rerank(
        self,
        *,
        query: str,
        chunks: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not chunks:
            return []

        self._init_model()
        if self._model is None:
            return chunks[:top_k]

        pairs = [(query, chunk.get("payload", {}).get("content", "")) for chunk in chunks]
        scores = self._model.predict(pairs)

        reranked = []
        for chunk, score in zip(chunks, scores, strict=False):
            reranked.append({
                **chunk,
                "score": float(score),
                "original_score": chunk.get("score", 0.0),
            })

        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_k]
