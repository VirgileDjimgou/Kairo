from __future__ import annotations

from pathlib import Path


SUPPORTED_TEXT_EXTENSIONS = {"txt", "md"}


def parse_document_bytes(file_bytes: bytes, file_name: str) -> str:
    extension = Path(file_name).suffix.lower().lstrip(".")
    if extension not in SUPPORTED_TEXT_EXTENSIONS:
        raise ValueError(f"Parser for .{extension} is not supported yet")

    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue

    raise ValueError("Could not decode document text")
