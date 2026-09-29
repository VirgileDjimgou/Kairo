from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.contexts.contracts import (
    ContextRequest,
    DomainContextProvider,
)
from app.modules.chat.contexts.providers.disciplinary import DisciplinaryContextProvider
from app.modules.chat.contexts.providers.documents import DocumentsContextProvider
from app.modules.chat.contexts.providers.events import EventsContextProvider
from app.modules.chat.contexts.providers.finance import FinanceContextProvider
from app.modules.chat.contexts.providers.governance import GovernanceContextProvider
from app.modules.chat.contexts.providers.membership import MembershipContextProvider
from app.modules.chat.payloads import StructuredContext


class ContextProviderRegistry:
    def __init__(self, providers: list[DomainContextProvider]) -> None:
        self._providers = list(providers)

    @property
    def providers(self) -> tuple[DomainContextProvider, ...]:
        return tuple(self._providers)

    async def collect_all(
        self, request: ContextRequest
    ) -> tuple[list[StructuredContext], str | None]:
        contexts: list[StructuredContext] = []
        for provider in self._providers:
            outcome = await provider.collect(request)
            if outcome.refusal is not None:
                return [], outcome.refusal
            if outcome.context is not None:
                contexts.append(outcome.context)
        return contexts, None


def build_default_registry(db: AsyncSession) -> ContextProviderRegistry:
    from app.modules.module_registry.descriptor import default_registry

    providers: list[DomainContextProvider] = [
        MembershipContextProvider(db),
        FinanceContextProvider(db),
        GovernanceContextProvider(db),
        DocumentsContextProvider(db),
        DisciplinaryContextProvider(db),
        EventsContextProvider(db),
    ]
    # Modules may optionally contribute AI context providers through their
    # descriptor; the core providers above stay authoritative and ordered first.
    providers.extend(default_registry().ai_context_providers(db))
    return ContextProviderRegistry(providers)
