"""Archive format shared by the worker, Windows scripts and tests.

The manifest is HMAC signed and the compressed payload is encrypted with a
Fernet deployment key.  A browser never receives either raw database content
or the encryption key.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_manifest(manifest: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in manifest.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sign_manifest(manifest: dict[str, Any], signing_key: str) -> dict[str, Any]:
    signed = dict(manifest)
    signed["signature"] = hmac.new(
        signing_key.encode("utf-8"), _canonical_manifest(signed), hashlib.sha256
    ).hexdigest()
    return signed


def verify_manifest(manifest: dict[str, Any], signing_key: str) -> bool:
    provided = str(manifest.get("signature", ""))
    expected = hmac.new(
        signing_key.encode("utf-8"), _canonical_manifest(manifest), hashlib.sha256
    ).hexdigest()
    return bool(provided) and hmac.compare_digest(provided, expected)


def encrypt_payload(payload: bytes, encryption_key: str) -> bytes:
    return Fernet(encryption_key.encode("utf-8")).encrypt(payload)


def decrypt_payload(payload: bytes, encryption_key: str) -> bytes:
    try:
        return Fernet(encryption_key.encode("utf-8")).decrypt(payload)
    except (ValueError, InvalidToken) as exc:
        raise ValueError(
            "Backup archive cannot be decrypted with the configured recovery key"
        ) from exc


def verify_archive_files(
    archive_path: Path, manifest_path: Path, *, encryption_key: str, signing_key: str
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not verify_manifest(manifest, signing_key):
        raise ValueError("Backup manifest signature is invalid")
    encrypted = archive_path.read_bytes()
    if sha256_bytes(encrypted) != manifest.get("archive_sha256"):
        raise ValueError("Backup archive SHA-256 checksum is invalid")
    # Decryption is also a cryptographic integrity check. Do not retain the
    # clear payload in this verification operation.
    decrypt_payload(encrypted, encryption_key)
    return manifest
