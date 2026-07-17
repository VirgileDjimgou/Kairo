from app.modules.chat.payloads import render_document_context
from app.modules.chat.prompting import build_prompt_context, build_retrieval_query, primary_role


def test_build_retrieval_query_keeps_language_topic_and_role_hints() -> None:
    query = build_retrieval_query(
        normalized_question="quels documents sont prets",
        response_language="fr",
        primary_role_code="secretary_general",
        topic="publication",
    )

    assert "quels documents sont prets" in query
    assert "publication" in query
    assert "documents" in query
    assert "français" in query


def test_build_prompt_context_preserves_role_and_structured_priority() -> None:
    prompt = build_prompt_context(
        question="Quel est mon solde ?",
        response_language="fr",
        primary_role_code=primary_role(["member"]),
        structured_block="[1] Personal contribution balance\nOutstanding balance: 75.00 EUR",
        document_block="No document sources were retrieved.",
        history_block="User: Bonjour",
    )

    assert "Role profile: member" in prompt.system_prompt
    assert "<structured_context>" in prompt.user_prompt
    assert "Outstanding balance: 75.00 EUR" in prompt.user_prompt
    assert "prefer them over document sources" in prompt.user_prompt


def test_render_document_context_returns_safe_fallback_when_empty() -> None:
    assert render_document_context([]) == "No document sources were retrieved."
