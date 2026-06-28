from __future__ import annotations

from io import BytesIO


def parse_pdf_bytes(file_bytes: bytes) -> str:
    import fitz

    document = fitz.open(stream=file_bytes, filetype="pdf")
    try:
        parts: list[str] = []
        for page in document:
            page_text = page.get_text("text").strip()
            if page_text:
                parts.append(page_text)
    finally:
        document.close()

    text = "\n\n".join(parts).strip()
    if not text:
        raise ValueError("No text content extracted from PDF")
    return text


def parse_docx_bytes(file_bytes: bytes) -> str:
    from docx import Document

    doc = Document(BytesIO(file_bytes))
    parts = [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]
    text = "\n".join(parts).strip()
    if not text:
        raise ValueError("No text content extracted from DOCX")
    return text
