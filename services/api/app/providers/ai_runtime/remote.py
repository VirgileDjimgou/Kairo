from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID

import httpx

from app.core.config import settings


class AiRuntimeUnavailableError(RuntimeError):
    """The optional local AI runtime cannot be reached safely."""


class _RemoteAiRuntimeClient:
    def __init__(self) -> None:
        if not settings.ai_gateway_base_url or not settings.ai_gateway_shared_secret:
            raise AiRuntimeUnavailableError("Assistant IA temporairement indisponible")
        self._base_url = settings.ai_gateway_base_url.rstrip("/")
        self._secret = settings.ai_gateway_shared_secret.encode("utf-8")

    @staticmethod
    def _body(payload: Any | None = None) -> str:
        return json.dumps(payload or {}, separators=(",", ":"), sort_keys=True)

    def _headers(self, method: str, path: str, body: str) -> dict[str, str]:
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        message = "\n".join((method.upper(), path, timestamp, nonce, body)).encode("utf-8")
        signature = hmac.new(self._secret, message, hashlib.sha256).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "X-Kairo-AI-Timestamp": timestamp,
            "X-Kairo-AI-Nonce": nonce,
            "X-Kairo-AI-Signature": signature,
        }
        if settings.ai_gateway_access_client_id and settings.ai_gateway_access_client_secret:
            headers["CF-Access-Client-Id"] = settings.ai_gateway_access_client_id
            headers["CF-Access-Client-Secret"] = settings.ai_gateway_access_client_secret
        return headers

    async def request(self, method: str, path: str, payload: Any | None = None) -> dict[str, Any]:
        body = self._body(payload)
        try:
            async with httpx.AsyncClient(timeout=settings.llm_request_timeout_seconds) as client:
                response = await client.request(
                    method,
                    f"{self._base_url}{path}",
                    headers=self._headers(method, path, body),
                    content=body,
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AiRuntimeUnavailableError("Assistant IA temporairement indisponible") from exc


class RemoteAiRuntimeLLMProvider(_RemoteAiRuntimeClient):
    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 2048,
    ) -> str:
        payload = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        result = await self.request("POST", "/v1/chat/completions", payload)
        content = str(result.get("content", "")).strip()
        if not content:
            raise AiRuntimeUnavailableError("Assistant IA temporairement indisponible")
        return content

    async def generate_stream(self, **kwargs: Any) -> AsyncGenerator[str, None]:
        # The cloud API owns the client SSE stream. The local runtime returns a
        # complete response, so the outer API can safely stream the result.
        yield await self.generate(**kwargs)


class RemoteAiRuntimeEmbeddingProvider(_RemoteAiRuntimeClient):
    def __init__(self) -> None:
        super().__init__()
        self._vector_size = settings.embedding_dimensions

    @property
    def vector_size(self) -> int:
        return self._vector_size

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        result = await self.request("POST", "/v1/embeddings", {"texts": texts})
        vectors = [[float(value) for value in vector] for vector in result.get("vectors", [])]
        if texts and len(vectors) != len(texts):
            raise AiRuntimeUnavailableError("Assistant IA temporairement indisponible")
        if vectors:
            self._vector_size = len(vectors[0])
        return vectors


class RemoteAiRuntimeVectorStoreProvider(_RemoteAiRuntimeClient):
    def ensure_collection(self, vector_size: int) -> None:
        self._sync("POST", "/v1/vectors/ensure-collection", {"vector_size": vector_size})

    def delete_vectors_for_version(self, tenant_id: UUID, document_version_id: UUID) -> None:
        self._sync(
            "POST",
            "/v1/vectors/delete-version",
            {"tenant_id": str(tenant_id), "document_version_id": str(document_version_id)},
        )

    def upsert_chunk_vectors(self, points: list[tuple[UUID, list[float], dict[str, Any]]]) -> None:
        self._sync(
            "POST",
            "/v1/vectors/upsert",
            {
                "points": [
                    {"id": str(point_id), "vector": vector, "payload": payload}
                    for point_id, vector, payload in points
                ]
            },
        )

    def search_chunk_vectors(
        self,
        *,
        tenant_id: UUID,
        query_vector: list[float],
        query_text: str | None = None,
        limit: int,
        score_threshold: float = 0.0,
        hybrid: bool = False,
    ) -> list[dict[str, Any]]:
        return list(
            self._sync(
                "POST",
                "/v1/vectors/search",
                {
                    "tenant_id": str(tenant_id),
                    "query_vector": query_vector,
                    "limit": limit,
                    "score_threshold": score_threshold,
                    "hybrid": hybrid,
                },
            ).get("results", [])
        )

    def _sync(self, method: str, path: str, payload: Any) -> dict[str, Any]:
        body = self._body(payload)
        try:
            with httpx.Client(timeout=settings.llm_request_timeout_seconds) as client:
                response = client.request(
                    method,
                    f"{self._base_url}{path}",
                    headers=self._headers(method, path, body),
                    content=body,
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AiRuntimeUnavailableError("Assistant IA temporairement indisponible") from exc
