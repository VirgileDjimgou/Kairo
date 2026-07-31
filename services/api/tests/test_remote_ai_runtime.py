from __future__ import annotations

import hashlib
import hmac
import importlib
import json

import pytest
from starlette.requests import Request

from app.core.config import Settings, settings
from app.providers.ai_runtime.remote import _RemoteAiRuntimeClient


def test_ai_runtime_can_be_explicitly_disabled() -> None:
    assert Settings(ai_runtime_mode="disabled").ai_runtime_enabled is False
    assert Settings(ai_runtime_mode="remote").ai_runtime_enabled is True


def test_remote_runtime_signs_the_exact_request_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ai_gateway_base_url", "https://ai.example.test")
    monkeypatch.setattr(settings, "ai_gateway_shared_secret", "test-shared-secret")
    monkeypatch.setattr(settings, "ai_gateway_access_client_id", "client-id")
    monkeypatch.setattr(settings, "ai_gateway_access_client_secret", "client-secret")
    monkeypatch.setattr("app.providers.ai_runtime.remote.time.time", lambda: 1_700_000_000)
    monkeypatch.setattr(
        "app.providers.ai_runtime.remote.uuid.uuid4", lambda: type("N", (), {"hex": "nonce"})()
    )

    client = _RemoteAiRuntimeClient()
    body = client._body({"tenant_id": "tenant", "limit": 6})
    headers = client._headers("POST", "/v1/vectors/search", body)

    expected = "\n".join(("POST", "/v1/vectors/search", "1700000000", "nonce", body))
    assert (
        headers["X-Kairo-AI-Signature"]
        == hmac.new(b"test-shared-secret", expected.encode("utf-8"), hashlib.sha256).hexdigest()
    )
    assert headers["CF-Access-Client-Id"] == "client-id"
    assert headers["CF-Access-Client-Secret"] == "client-secret"


@pytest.mark.asyncio
async def test_local_gateway_accepts_signed_requests_and_rejects_replay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_GATEWAY_SHARED_SECRET", "gateway-test-secret")
    gateway = importlib.import_module("ai_gateway.main")
    gateway.settings.ai_gateway_shared_secret = "gateway-test-secret"
    gateway._nonces.clear()
    monkeypatch.setattr(gateway.time, "time", lambda: 1_700_000_000)

    raw_body = json.dumps({"texts": ["test"]}, separators=(",", ":")).encode("utf-8")
    timestamp = "1700000000"
    nonce = "one-time-nonce"
    canonical = "\n".join(("POST", "/v1/embeddings", timestamp, nonce, raw_body.decode()))
    signature = hmac.new(
        b"gateway-test-secret", canonical.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": raw_body, "more_body": False}

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/v1/embeddings",
            "headers": [
                (b"x-kairo-ai-timestamp", timestamp.encode()),
                (b"x-kairo-ai-nonce", nonce.encode()),
                (b"x-kairo-ai-signature", signature.encode()),
            ],
        },
        receive,
    )
    assert await gateway._verify_request(request) == {"texts": ["test"]}

    replay_request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/v1/embeddings",
            "headers": [
                (b"x-kairo-ai-timestamp", timestamp.encode()),
                (b"x-kairo-ai-nonce", nonce.encode()),
                (b"x-kairo-ai-signature", signature.encode()),
            ],
        },
        receive,
    )
    with pytest.raises(Exception, match="Replayed AI gateway request"):
        await gateway._verify_request(replay_request)
