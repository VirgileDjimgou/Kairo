from __future__ import annotations

import re

_TOKEN_PATTERN = re.compile(r"[a-z0-9à-ÿ]{3,}", re.IGNORECASE)
_STOPWORDS = {
    "about",
    "avec",
    "avec",
    "dans",
    "de",
    "der",
    "des",
    "die",
    "document",
    "documents",
    "ein",
    "eine",
    "for",
    "les",
    "mais",
    "mit",
    "oder",
    "pour",
    "que",
    "qui",
    "sur",
    "the",
    "une",
    "what",
    "which",
}


def extract_rank_terms(text: str) -> list[str]:
    unique_terms: list[str] = []
    seen: set[str] = set()
    for raw in _TOKEN_PATTERN.findall(text.lower()):
        if raw in _STOPWORDS:
            continue
        if raw in seen:
            continue
        seen.add(raw)
        unique_terms.append(raw)
    return unique_terms


def compute_keyword_overlap_ratio(*, query: str, content: str) -> float:
    query_terms = extract_rank_terms(query)
    if not query_terms:
        return 0.0
    content_terms = set(extract_rank_terms(content))
    if not content_terms:
        return 0.0
    matches = sum(1 for term in query_terms if term in content_terms)
    return matches / len(query_terms)
