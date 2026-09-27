from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.modules.chat.domain_policy import ChatDomainPolicy
from app.modules.chat.payloads import StructuredContext


@dataclass(frozen=True, slots=True)
class ContextRequest:
    tenant_id: UUID
    user_id: UUID
    capabilities: tuple[str, ...]
    question: str
    normalized_question: str
    response_language: str
    domain_policy: ChatDomainPolicy


@dataclass(frozen=True, slots=True)
class ContextOutcome:
    context: StructuredContext | None = None
    refusal: str | None = None


class DomainContextProvider(Protocol):
    key: str

    async def collect(self, request: ContextRequest) -> ContextOutcome: ...
