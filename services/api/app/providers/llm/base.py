from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Protocol


class LLMProvider(Protocol):
    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 2048,
    ) -> str: ...

    def generate_stream(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]: ...
