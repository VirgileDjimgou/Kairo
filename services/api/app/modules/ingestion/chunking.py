from __future__ import annotations


def estimate_token_count(text: str) -> int:
    # rough enough for chunk metadata until we wire a real tokenizer
    return max(1, len(text.split()))


def chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(cleaned):
            break
        start = max(end - chunk_overlap, start + 1)

    return chunks
