from __future__ import annotations

import re

WHATSAPP_LINE_PATTERN = re.compile(
    r"^\[?(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\]?"
    r"\s*[-–]?\s*(?P<sender>[^:]+):\s*(?P<message>.+)$"
)


def parse_whatsapp_export(file_bytes: bytes) -> str:
    text = _decode_text(file_bytes)
    lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = WHATSAPP_LINE_PATTERN.match(line)
        if match:
            sender = match.group("sender").strip()
            message = match.group("message").strip()
            lines.append(f"{sender}: {message}")
        elif lines:
            lines[-1] = f"{lines[-1]} {line}"
        else:
            lines.append(line)

    if not lines:
        raise ValueError("No WhatsApp messages found in export")

    return "\n".join(lines)


def _decode_text(file_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode WhatsApp export")
