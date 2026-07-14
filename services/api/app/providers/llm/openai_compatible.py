from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

from app.core.config import settings


class OpenAICompatibleLLMProvider:
    """Chat provider for OpenAI-compatible local servers such as LM Studio."""

    def __init__(self) -> None:
        self._timeout = settings.llm_request_timeout_seconds

    def _headers(self) -> dict[str, str]:
        api_key = settings.openai_compatible_api_key.strip()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    @staticmethod
    def _extract_message_content(message: dict[str, object]) -> str | None:
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()

        reasoning = message.get("reasoning_content")
        if isinstance(reasoning, str) and reasoning.strip():
            markers = [
                "Final Output:",
                "Final answer:",
                "Answer:",
                "Réponse finale :",
                "Réponse finale:",
            ]
            for marker in markers:
                if marker in reasoning:
                    tail = reasoning.split(marker, 1)[1].strip()
                    if tail:
                        return tail
            return reasoning.strip()

        return None

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
            base_url=settings.openai_compatible_base_url,
            timeout=self._timeout,
            headers=self._headers(),
        ) as client:
            response = await client.post(
                "/chat/completions",
                json={
                    "model": settings.openai_compatible_llm_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            payload = response.json()
            choices = payload.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                content = self._extract_message_content(message)
                if content:
                    return content
            raise ValueError("OpenAI-compatible server returned an empty chat response")

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
            base_url=settings.openai_compatible_base_url,
            timeout=self._timeout,
            headers=self._headers(),
        ) as client:
            async with client.stream(
                "POST",
                "/chat/completions",
                json={
                    "model": settings.openai_compatible_llm_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": True,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip() or not line.startswith("data: "):
                        continue
                    data = line.removeprefix("data: ").strip()
                    if data == "[DONE]":
                        return
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    token = delta.get("content", "")
                    if token:
                        yield str(token)
