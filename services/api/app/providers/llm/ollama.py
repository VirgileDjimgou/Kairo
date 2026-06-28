from __future__ import annotations

import httpx

from app.core.config import settings


class OllamaLLMProvider:
    def __init__(self) -> None:
        self._timeout = settings.embedding_request_timeout_seconds

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
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
                },
            )
            response.raise_for_status()
            payload = response.json()
            message = payload.get("message", {})
            content = message.get("content")
            if not content:
                raise ValueError("Ollama returned an empty chat response")
            return str(content)
