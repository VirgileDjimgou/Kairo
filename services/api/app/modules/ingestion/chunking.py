from __future__ import annotations

import re


def estimate_token_count(text: str) -> int:
    return max(1, len(text.split()))


def chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    return _recursive_split(cleaned, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def _recursive_split(text: str, *, chunk_size: int, chunk_overlap: int) -> list[str]:
    separators = [
        r"\n\n+",       # paragraph boundaries
        r"\n",           # line boundaries
        r"(?<=[.!?])\s+",  # sentence boundaries
        r"(?<=[;:])\s+",  # clause boundaries
        r"\s{2,}",       # multi-space
        r"\s",           # word boundaries (fallback)
    ]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end >= len(text):
            piece = text[start:].strip()
            if piece:
                chunks.append(piece)
            break

        # Try to find a natural break point near chunk_size
        best_break = end
        for sep in separators:
            candidate = _find_break_before(text, end, sep)
            if candidate is not None and candidate > start:
                best_break = candidate
                break

        # Ensure we don't create a tiny last chunk
        if best_break - start < chunk_size // 3 and len(chunks) > 0:
            best_break = end

        piece = text[start:best_break].strip()
        if piece:
            chunks.append(piece)

        start = max(best_break - chunk_overlap, start + 1)

        if start >= len(text):
            break

    return chunks


def _find_break_before(text: str, position: int, pattern: str) -> int | None:
    """Find the last separator match ending at or before position."""
    segment = text[:position]
    matches = list(re.finditer(pattern, segment))
    if not matches:
        return None
    return matches[-1].end()
