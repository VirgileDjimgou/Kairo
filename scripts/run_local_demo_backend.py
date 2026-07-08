from __future__ import annotations

"""
Run the Kairo API locally with the demo SQLite database and fake external providers.

This helper is intended for visual audits and offline validation when Docker or the
full production stack is not available on the local machine.

Usage:
    python scripts/run_local_demo_backend.py
"""

import asyncio
import importlib.util
import os
import sys
from pathlib import Path

import uvicorn


REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "services" / "api"
TESTS_ROOT = API_ROOT / "tests"
SQLITE_DB_PATH = API_ROOT / "kairo-local.sqlite3"


def _configure_environment() -> None:
    os.environ.setdefault(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{SQLITE_DB_PATH.as_posix()}",
    )
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("APP_DEBUG", "true")
    os.environ.setdefault("INDEXING_AUTO_ENABLED", "false")
    os.environ.setdefault("INGESTION_AUTO_ENQUEUE", "false")


def _ensure_import_path() -> None:
    for path in (str(API_ROOT), str(TESTS_ROOT)):
        if path not in sys.path:
            sys.path.insert(0, path)


def _load_test_fakes():
    fakes_path = TESTS_ROOT / "fakes.py"
    spec = importlib.util.spec_from_file_location("kairo_local_fakes", fakes_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load test fakes from {fakes_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LocalReranker:
    def rerank(self, *, query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
        ranked = sorted(
            chunks,
            key=lambda item: (float(item.get("score", 0.0)), str(item.get("id", ""))),
            reverse=True,
        )
        return ranked[:top_k]


class LocalAuditLlmProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def _reply_for_prompt(self, user_prompt: str) -> str:
        if "Response language: de" in user_prompt:
            return "Antwort auf Grundlage autorisierter Quellen."
        if "Response language: fr" in user_prompt:
            return "Réponse fondée sur des sources autorisées."
        return "Grounded answer from authorized sources."

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 2048,
    ) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return self._reply_for_prompt(user_prompt)

    async def generate_stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 2048,
    ):
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        reply = self._reply_for_prompt(user_prompt)
        for token in reply.split(" "):
            yield f"{token} "


async def _prepare_database() -> None:
    from app.db.base import Base
    from app.db.seed import seed_database
    from app.db.session import engine
    import app.db.models  # noqa: F401 - register ORM models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_database()


async def _main() -> None:
    _configure_environment()
    _ensure_import_path()

    from app.core.dependencies import (
        get_embedding_provider,
        get_llm_provider,
        get_notification_providers,
        get_object_storage_provider,
        get_reranker_provider,
        get_vector_store_provider,
    )
    from app.main import app

    fakes = _load_test_fakes()

    # The object storage provider only needs the upload/download interface;
    # the local demo does not upload files, so a tiny in-memory helper is enough.
    class FakeObjectStorageProvider:
        def __init__(self) -> None:
            self.uploads: list[dict] = []

        def ensure_bucket(self, bucket: str) -> None:
            return None

        def upload_bytes(self, bucket: str, object_key: str, data: bytes, content_type: str) -> str:
            self.uploads.append(
                {
                    "bucket": bucket,
                    "object_key": object_key,
                    "data": data,
                    "content_type": content_type,
                }
            )
            return object_key

        def download_bytes(self, bucket: str, object_key: str) -> bytes:
            for item in self.uploads:
                if item["bucket"] == bucket and item["object_key"] == object_key:
                    return item["data"]
            raise FileNotFoundError(f"Object not found: {bucket}/{object_key}")

    app.dependency_overrides[get_object_storage_provider] = lambda: FakeObjectStorageProvider()
    app.dependency_overrides[get_embedding_provider] = lambda: fakes.FakeEmbeddingProvider()
    app.dependency_overrides[get_vector_store_provider] = lambda: fakes.FakeVectorStoreProvider()
    app.dependency_overrides[get_llm_provider] = lambda: LocalAuditLlmProvider()
    app.dependency_overrides[get_reranker_provider] = lambda: LocalReranker()
    app.dependency_overrides[get_notification_providers] = lambda: [fakes.FakeEmailNotificationProvider()]

    await _prepare_database()

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True,
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(_main())
