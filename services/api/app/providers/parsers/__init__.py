from __future__ import annotations

from pathlib import Path

from app.providers.parsers.pdf_docx import parse_docx_bytes, parse_pdf_bytes
from app.providers.parsers.whatsapp import parse_whatsapp_export

TEXT_EXTENSIONS = {"txt", "md", "csv"}
WHATSAPP_EXTENSIONS = {"whatsapp.txt"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def parse_document_bytes(file_bytes: bytes, file_name: str) -> str:
    extension = _resolve_extension(file_name)

    if extension in TEXT_EXTENSIONS:
        return _parse_plain_text(file_bytes)
    if extension == "pdf":
        return parse_pdf_bytes(file_bytes)
    if extension == "docx":
        return parse_docx_bytes(file_bytes)
    if extension in WHATSAPP_EXTENSIONS or _looks_like_whatsapp_export(file_name, file_bytes):
        return parse_whatsapp_export(file_bytes)
    if extension in IMAGE_EXTENSIONS:
        raise ValueError("OCR is not configured yet for image documents")

    raise ValueError(f"Parser for .{extension} is not supported yet")


def _resolve_extension(file_name: str) -> str:
    name = Path(file_name or "").name.lower()
    if name.endswith(".whatsapp.txt"):
        return "whatsapp.txt"
    return Path(name).suffix.lstrip(".")


def _looks_like_whatsapp_export(file_name: str, file_bytes: bytes) -> bool:
    if "whatsapp" in file_name.lower():
        return True
    sample = file_bytes[:500].decode("utf-8", errors="ignore")
    return " - " in sample and ":" in sample and "/" in sample


def _parse_plain_text(file_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode document text")
