from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import httpx

from app.core.config import settings


class OllamaLLMProvider:
    def __init__(self) -> None:
        self._timeout = settings.llm_request_timeout_seconds

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 2048,
    ) -> str:
        async with httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=self._timeout,
        ) as client:
            response = await client.post(
                "/api/chat",
                json={
                    "model": settings.ollama_llm_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            payload = response.json()
            message = payload.get("message", {})
            content = message.get("content")
            if not content:
                raise ValueError("Ollama returned an empty chat response")
            return str(content)

    async def generate_stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=self._timeout,
        ) as client:
            async with client.stream(
                "POST",
                "/api/chat",
                json={
                    "model": settings.ollama_llm_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens,
                    },
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if chunk.get("done"):
                        return
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
