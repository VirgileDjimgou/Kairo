from __future__ import annotations

from typing import Any


def compute_confidence_score(
    chunks: list[dict[str, Any]],
    *,
    rerank_enabled: bool = False,
) -> float:
    """Compute a single confidence score for the retrieved chunk set.

    Returns a value between 0.0 and 1.0 indicating overall retrieval quality.
    """
    if not chunks:
        return 0.0

    scores = [c.get("score", 0.0) for c in chunks]
    if not scores:
        return 0.0

    max_score = max(scores)
    mean_score = sum(scores) / len(scores)

    # Base confidence: average score weighted by top score signal
    base = mean_score * 0.6 + max_score * 0.4

    # Penalize if only one weak chunk
    if len(chunks) == 1 and max_score < 0.5:
        base *= 0.5

    # Boost if reranker produced consistent high scores
    if rerank_enabled and max_score > 0.7:
        base = min(1.0, base * 1.15)

    return round(max(0.0, min(1.0, base)), 4)
