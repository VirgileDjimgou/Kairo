from app.modules.rag.ranking import compute_keyword_overlap_ratio, extract_rank_terms


def test_extract_rank_terms_deduplicates_and_skips_stopwords() -> None:
    terms = extract_rank_terms("What documents explain cotisations et reglement interieur?")
    assert "what" not in terms
    assert "documents" not in terms
    assert "cotisations" in terms
    assert "reglement" in terms


def test_compute_keyword_overlap_ratio_rewards_matching_terms() -> None:
    score = compute_keyword_overlap_ratio(
        query="cotisations reglement interieur",
        content="Le reglement interieur explique les cotisations annuelles.",
    )
    assert score > 0.6


def test_compute_keyword_overlap_ratio_returns_zero_without_terms() -> None:
    score = compute_keyword_overlap_ratio(
        query="the and for",
        content="General policy text without useful overlap.",
    )
    assert score == 0.0
