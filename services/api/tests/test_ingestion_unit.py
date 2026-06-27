"""Unit tests for ingestion parsers and chunking."""

from app.modules.ingestion.chunking import chunk_text, estimate_token_count
from app.modules.ingestion.parsers import parse_document_bytes


def test_parse_txt_bytes() -> None:
    text = parse_document_bytes(b"Hello tenant policy", "notes.txt")
    assert text == "Hello tenant policy"


def test_parse_markdown_bytes() -> None:
    text = parse_document_bytes(b"# Title\n\nBody", "guide.md")
    assert "Title" in text


def test_unsupported_extension_raises() -> None:
    try:
        parse_document_bytes(b"%PDF", "report.pdf")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "not supported yet" in str(exc).lower()


def test_chunk_text_splits_long_content() -> None:
    content = "word " * 500
    chunks = chunk_text(content.strip(), chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_estimate_token_count_is_positive() -> None:
    assert estimate_token_count("one two three") == 3
