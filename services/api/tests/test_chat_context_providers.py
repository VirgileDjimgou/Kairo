"""Regression coverage for the chat domain context provider registry (Sprint 112)."""

import uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.contexts.contracts import ContextOutcome, ContextRequest
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.providers.disciplinary import DisciplinaryContextProvider
from app.modules.chat.contexts.providers.documents import DocumentsContextProvider
from app.modules.chat.contexts.providers.events import EventsContextProvider
from app.modules.chat.contexts.providers.finance import FinanceContextProvider
from app.modules.chat.contexts.providers.governance import GovernanceContextProvider
from app.modules.chat.contexts.providers.membership import MembershipContextProvider
from app.modules.chat.contexts.registry import ContextProviderRegistry, build_default_registry
from app.modules.chat.domain_policy import ChatDomainPolicy
from app.modules.chat.payloads import StructuredContext
from app.modules.contributions.repository import ContributionRepository

pytestmark = pytest.mark.asyncio


def _policy(**overrides: bool) -> ChatDomainPolicy:
    values = {
        "member_finance": False,
        "tenant_finance": False,
        "governance": False,
        "publication": False,
        "disciplinary": False,
        "sports": False,
    }
    values.update(overrides)
    return ChatDomainPolicy(**values)


def _request(
    *,
    tenant_id=None,
    user_id=None,
    question: str,
    normalized_question: str | None = None,
    policy: ChatDomainPolicy | None = None,
    language: str = "en",
) -> ContextRequest:
    return ContextRequest(
        tenant_id=tenant_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        capabilities=(),
        question=question,
        normalized_question=normalized_question or question,
        response_language=language,
        domain_policy=policy or _policy(),
    )


class _RecordingProvider:
    def __init__(self, key: str, outcome: ContextOutcome) -> None:
        self.key = key
        self._outcome = outcome
        self.calls = 0

    async def collect(self, request: ContextRequest) -> ContextOutcome:
        self.calls += 1
        return self._outcome


async def test_registry_runs_providers_in_order_and_stops_on_refusal() -> None:
    first = _RecordingProvider(
        "first",
        ContextOutcome(
            context=StructuredContext(source_type="structured:first", title="First", content="one")
        ),
    )
    second = _RecordingProvider("second", ContextOutcome(refusal="blocked"))
    third = _RecordingProvider(
        "third",
        ContextOutcome(
            context=StructuredContext(source_type="structured:third", title="Third", content="three")
        ),
    )
    registry = ContextProviderRegistry([first, second, third])

    contexts, refusal = await registry.collect_all(_request(question="anything"))

    assert refusal == "blocked"
    assert contexts == []
    assert first.calls == 1
    assert second.calls == 1
    assert third.calls == 0


async def test_default_registry_exposes_the_domain_providers_in_stable_order(
    db_session: AsyncSession,
) -> None:
    registry = build_default_registry(db_session)
    assert [provider.key for provider in registry.providers] == [
        "membership",
        "finance",
        "governance",
        "documents",
        "disciplinary",
        "events",
    ]


async def test_providers_refuse_matching_questions_without_authorization(
    db_session: AsyncSession,
) -> None:
    cases = [
        (MembershipContextProvider(db_session), "what is my balance", "personal_finance_forbidden"),
        (FinanceContextProvider(db_session), "finance summary", "tenant_finance_forbidden"),
        (GovernanceContextProvider(db_session), "governance summary", "governance_forbidden"),
        (DocumentsContextProvider(db_session), "publication context", "publication_forbidden"),
        (DisciplinaryContextProvider(db_session), "open cases", "disciplinary_forbidden"),
        (EventsContextProvider(db_session), "sports schedule", "sports_forbidden"),
    ]

    for provider, question, refusal_key in cases:
        outcome = await provider.collect(_request(question=question))
        assert outcome.refusal == message(refusal_key, "en"), provider.key
        assert outcome.context is None, provider.key


async def test_providers_ignore_unrelated_questions_without_querying(
    db_session: AsyncSession,
) -> None:
    allowed = _policy(
        member_finance=True,
        tenant_finance=True,
        governance=True,
        publication=True,
        disciplinary=True,
        sports=True,
    )
    providers = [
        MembershipContextProvider(db_session),
        FinanceContextProvider(db_session),
        GovernanceContextProvider(db_session),
        DocumentsContextProvider(db_session),
        DisciplinaryContextProvider(db_session),
        EventsContextProvider(db_session),
    ]

    for provider in providers:
        outcome = await provider.collect(
            _request(question="what is the weather", policy=allowed)
        )
        assert outcome == ContextOutcome(), provider.key


async def test_authorized_providers_return_tenant_scoped_contexts(
    db_session: AsyncSession,
) -> None:
    tenant_a = await create_tenant_with_user(db_session, f"ctx-a-{uuid.uuid4().hex[:6]}")
    tenant_b = await create_tenant_with_user(db_session, f"ctx-b-{uuid.uuid4().hex[:6]}")
    member_a = await create_user_for_tenant(
        db_session,
        tenant_id=tenant_a["tenant"].id,
        email=f"member-a-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass123!",
        display_name="Member A",
        role_code="member",
        profile_type="member",
        member_code=f"CA-{uuid.uuid4().hex[:4].upper()}",
    )
    repo = ContributionRepository(db_session)
    await repo.create_contribution(
        tenant_a["tenant"].id,
        {
            "membership_profile_id": member_a["profile"].id,
            "year": 2026,
            "expected_amount": "60.00",
            "paid_amount": "0.00",
            "currency": "EUR",
            "status": "pending",
        },
    )
    await db_session.commit()

    allowed = _policy(member_finance=True, tenant_finance=True, governance=True)

    membership_outcome = await MembershipContextProvider(db_session).collect(
        _request(
            tenant_id=tenant_a["tenant"].id,
            user_id=member_a["user"].id,
            question="what is my balance",
            policy=allowed,
        )
    )
    assert membership_outcome.refusal is None
    assert membership_outcome.context is not None
    assert membership_outcome.context.source_type == "structured:member_balance"
    assert "Member A" in membership_outcome.context.content
    assert "Total expected: 60.00 EUR" in membership_outcome.context.content

    finance_outcome = await FinanceContextProvider(db_session).collect(
        _request(
            tenant_id=tenant_a["tenant"].id,
            question="finance summary",
            policy=allowed,
        )
    )
    assert finance_outcome.refusal is None
    assert finance_outcome.context is not None
    assert "Total expected: 60.00 EUR" in finance_outcome.context.content

    other_tenant_outcome = await FinanceContextProvider(db_session).collect(
        _request(
            tenant_id=tenant_b["tenant"].id,
            question="finance summary",
            policy=allowed,
        )
    )
    assert other_tenant_outcome.context is not None
    assert "Total expected: 0.00 EUR" in other_tenant_outcome.context.content

    governance_outcome = await GovernanceContextProvider(db_session).collect(
        _request(
            tenant_id=tenant_a["tenant"].id,
            question="governance summary",
            policy=allowed,
        )
    )
    assert governance_outcome.refusal is None
    assert governance_outcome.context is not None
    assert "Members in tenant: 1" in governance_outcome.context.content

    other_governance = await GovernanceContextProvider(db_session).collect(
        _request(
            tenant_id=tenant_b["tenant"].id,
            question="governance summary",
            policy=allowed,
        )
    )
    assert other_governance.context is not None
    assert "Members in tenant: 0" in other_governance.context.content
