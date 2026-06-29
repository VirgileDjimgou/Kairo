from __future__ import annotations

import csv
import io
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel


class ImportRowError(BaseModel):
    row_number: int
    message: str
    column: str | None = None
    value: str | None = None


class ImportResult(BaseModel):
    total_rows: int
    success_count: int
    error_count: int
    errors: list[ImportRowError]
    dry_run: bool


def parse_csv(content: bytes) -> list[dict[str, str]]:
    """Parse raw CSV bytes into a list of row dicts."""
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def generate_csv(
    rows: Sequence[dict[str, Any]],
    fieldnames: list[str] | None = None,
) -> str:
    """Generate a CSV string from a list of dicts."""
    if not rows:
        return ""
    names = fieldnames or list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=names, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
