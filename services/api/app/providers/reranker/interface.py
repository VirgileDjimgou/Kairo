from __future__ import annotations

from typing import Any, Protocol


class RerankerProvider(Protocol):
    """Cross-encoder reranker that re-scores retrieved chunks."""

    def rerank(
        self,
        *,
        query: str,
        chunks: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]: ...
