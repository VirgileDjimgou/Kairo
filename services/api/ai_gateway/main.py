from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections import deque
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.ai-local", extra="ignore")

    ai_gateway_shared_secret: str
    ai_gateway_request_ttl_seconds: int = 60
    ollama_base_url: str = "http://ollama:11434"
    ollama_llm_model: str = "qwen2.5:7b-instruct"
    ollama_embedding_model: str = "nomic-embed-text"
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "orgmind_document_chunks"
    embedding_dimensions: int = 768
    ai_embedding_profile: str | None = None


settings = GatewaySettings()
app = FastAPI(title="Kairo private AI runtime gateway", docs_url=None, redoc_url=None)
_nonces: deque[tuple[int, str]] = deque(maxlen=5000)


async def _verify_request(request: Request) -> dict[str, Any]:
    raw_body = await request.body()
    timestamp = request.headers.get("X-Kairo-AI-Timestamp", "")
    nonce = request.headers.get("X-Kairo-AI-Nonce", "")
    signature = request.headers.get("X-Kairo-AI-Signature", "")
    try:
        sent_at = int(timestamp)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid AI gateway request") from exc
    now = int(time.time())
    if not nonce or abs(now - sent_at) > settings.ai_gateway_request_ttl_seconds:
        raise HTTPException(status_code=401, detail="Expired AI gateway request")
    while _nonces and now - _nonces[0][0] > settings.ai_gateway_request_ttl_seconds:
        _nonces.popleft()
    if any(existing_nonce == nonce for _, existing_nonce in _nonces):
        raise HTTPException(status_code=401, detail="Replayed AI gateway request")
    canonical = "\n".join(
        (request.method.upper(), request.url.path, timestamp, nonce, raw_body.decode("utf-8"))
    ).encode("utf-8")
    expected = hmac.new(
        settings.ai_gateway_shared_secret.encode("utf-8"), canonical, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid AI gateway signature")
    _nonces.append((now, nonce))
    try:
        return json.loads(raw_body or b"{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc


class ChatRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = Field(default=1024, ge=1, le=4096)


@app.get("/health")
async def health(request: Request) -> dict[str, Any]:
    await _verify_request(request)
    try:
        qdrant = QdrantClient(url=settings.qdrant_url, timeout=3)
        qdrant.get_collections()
        async with httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=3) as client:
            response = await client.get("/api/tags")
            response.raise_for_status()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Local AI runtime unavailable") from exc
    return {
        "status": "ok",
        "embedding_profile": settings.ai_embedding_profile or settings.ollama_embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> dict[str, str]:
    payload = ChatRequest.model_validate(await _verify_request(request))
    try:
        async with httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=180) as client:
            response = await client.post(
                "/api/chat",
                json={
                    "model": settings.ollama_llm_model,
                    "messages": [
                        {"role": "system", "content": payload.system_prompt},
                        {"role": "user", "content": payload.user_prompt},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": payload.temperature,
                        "top_p": payload.top_p,
                        "num_predict": payload.max_tokens,
                    },
                },
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Local AI runtime unavailable") from exc
    return {"content": str(content)}


@app.post("/v1/embeddings")
async def embeddings(request: Request) -> dict[str, list[list[float]]]:
    payload = await _verify_request(request)
    texts = payload.get("texts")
    if not isinstance(texts, list) or not all(isinstance(text, str) for text in texts):
        raise HTTPException(status_code=422, detail="texts must be a string list")
    vectors: list[list[float]] = []
    try:
        async with httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=180) as client:
            for text in texts:
                response = await client.post(
                    "/api/embed", json={"model": settings.ollama_embedding_model, "input": text}
                )
                response.raise_for_status()
                vector = response.json().get("embeddings", [[]])[0]
                vectors.append([float(value) for value in vector])
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Local AI runtime unavailable") from exc
    return {"vectors": vectors}


def _qdrant() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url, timeout=30)


@app.post("/v1/vectors/ensure-collection")
async def ensure_collection(request: Request) -> dict[str, bool]:
    payload = await _verify_request(request)
    vector_size = int(payload.get("vector_size", 0))
    if vector_size <= 0:
        raise HTTPException(status_code=422, detail="A positive vector size is required")
    client = _qdrant()
    existing = {item.name for item in client.get_collections().collections}
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    else:
        collection = client.get_collection(settings.qdrant_collection)
        vectors = collection.config.params.vectors
        existing_size = getattr(vectors, "size", None)
        if existing_size != vector_size:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Embedding profile or vector dimension changed; reindex the local "
                    "Qdrant collection before continuing"
                ),
            )
    return {"ok": True}


@app.post("/v1/vectors/delete-version")
async def delete_version(request: Request) -> dict[str, bool]:
    payload = await _verify_request(request)
    client = _qdrant()
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[
                FieldCondition(key="tenant_id", match=MatchValue(value=str(payload["tenant_id"]))),
                FieldCondition(
                    key="document_version_id",
                    match=MatchValue(value=str(payload["document_version_id"])),
                ),
            ]
        ),
    )
    return {"ok": True}


@app.post("/v1/vectors/upsert")
async def upsert(request: Request) -> dict[str, bool]:
    payload = await _verify_request(request)
    points = [
        PointStruct(id=str(item["id"]), vector=item["vector"], payload=item["payload"])
        for item in payload.get("points", [])
    ]
    if points:
        _qdrant().upsert(collection_name=settings.qdrant_collection, points=points)
    return {"ok": True}


@app.post("/v1/vectors/search")
async def search(request: Request) -> dict[str, list[dict[str, Any]]]:
    payload = await _verify_request(request)
    result = _qdrant().query_points(
        collection_name=settings.qdrant_collection,
        query=payload["query_vector"],
        query_filter=Filter(
            must=[
                FieldCondition(key="tenant_id", match=MatchValue(value=str(payload["tenant_id"])))
            ]
        ),
        limit=int(payload["limit"]),
        with_payload=True,
        score_threshold=float(payload.get("score_threshold", 0)) or None,
    )
    points = getattr(result, "points", result)
    return {
        "results": [
            {
                "id": str(point.id),
                "score": float(point.score or 0),
                "payload": point.payload or {},
                "retrieval_mode": "dense",
            }
            for point in points
        ]
    }
