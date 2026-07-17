from __future__ import annotations

from pathlib import Path

LANGUAGE_HINTS: dict[str, tuple[str, ...]] = {
    "fr": (
        "_fr",
        "bonjour",
        "association",
        "cotisation",
        "cotisations",
        "adhesion",
        "adhésion",
        "procès-verbal",
        "proces-verbal",
        "compte rendu",
        "règlement",
        "reglement",
        "sanction",
        "mise en demeure",
        "bilan",
        "rapport",
    ),
    "en": (
        "_en",
        "hello",
        "membership",
        "financial report",
        "treasurer",
        "minutes",
        "governance",
        "disciplinary",
        "annual report",
        "review of activities",
    ),
    "de": (
        "_de",
        "hallo",
        "satzung",
        "verein",
        "beitrag",
        "beiträge",
        "vorstand",
        "protokoll",
        "verhaltenskodex",
        "anerkennung",
        "fußball",
        "fussball",
    ),
}

FINANCE_TOKENS = (
    "audit",
    "auditor",
    "budget",
    "bilan",
    "comptes",
    "contribution",
    "contributions",
    "cotisation",
    "cotisations",
    "finance",
    "financial report",
    "invoice",
    "journal",
    "ledger",
    "payment",
    "rapport financier",
    "receipt",
    "synthese",
    "synthèse",
    "trésorerie",
    "tresorerie",
)

DISCIPLINARY_TOKENS = (
    "avertissement",
    "cahier des sanctions",
    "complaint",
    "disciplin",
    "exclusion",
    "grievance",
    "incident",
    "mise_en_demeure",
    "mise en demeure",
    "sanction",
    "warning",
)

GOVERNANCE_TOKENS = (
    "board",
    "bureau",
    "catalogue des compétences",
    "catalogue des competences",
    "confidential",
    "election",
    "minutes",
    "plan d'action",
    "plan d actions",
    "plan d’actions",
    "policy draft",
    "procès-verbal",
    "proces-verbal",
    "programme d'assistance",
    "programme d assistance",
    "pv",
    "resolution",
    "secretariat",
    "secretary",
    "strategy",
    "vorstand",
)


def normalize_language(value: str | None) -> str:
    if not value:
        return "und"
    lowered = value.strip().lower()
    if lowered.startswith("fr"):
        return "fr"
    if lowered.startswith("en"):
        return "en"
    if lowered.startswith("de"):
        return "de"
    if lowered in {"und", "unknown", "undetermined"}:
        return "und"
    return "und"


def infer_document_language(
    *,
    file_name: str | None,
    title: str | None = None,
    description: str | None = None,
    text_sample: str | None = None,
) -> str:
    sample_parts = [file_name or "", title or "", description or "", text_sample or ""]
    haystack = " ".join(sample_parts).lower()
    scores = {
        language: sum(1 for token in tokens if token in haystack)
        for language, tokens in LANGUAGE_HINTS.items()
    }
    best_language = max(scores, key=scores.get)
    best_score = scores[best_language]
    if best_score == 0:
        return "und"
    if list(scores.values()).count(best_score) > 1:
        return "und"
    return best_language


def infer_document_language_from_upload(
    *,
    file_name: str | None,
    title: str | None = None,
    description: str | None = None,
    file_bytes: bytes | None = None,
) -> str:
    text_sample = _extract_text_sample(file_name=file_name, file_bytes=file_bytes)
    return infer_document_language(
        file_name=file_name,
        title=title,
        description=description,
        text_sample=text_sample,
    )


def classify_archive_access(file_name: str, roles: dict[str, str]) -> tuple[str, list[str]]:
    lower = file_name.lower()
    finance_roles = _role_ids(
        roles,
        "treasurer",
        "auditor",
        "president",
        "vice_president",
        "principal_admin",
        "admin",
    )
    discipline_roles = _role_ids(
        roles,
        "censor",
        "president",
        "vice_president",
        "principal_admin",
        "admin",
    )
    governance_roles = _role_ids(
        roles,
        "secretary_general",
        "president",
        "vice_president",
        "principal_admin",
        "admin",
    )

    if any(token in lower for token in DISCIPLINARY_TOKENS):
        return "role_restricted", discipline_roles
    if any(token in lower for token in FINANCE_TOKENS):
        return "role_restricted", finance_roles
    if any(token in lower for token in GOVERNANCE_TOKENS):
        return "role_restricted", governance_roles
    return "tenant_public", []


def _extract_text_sample(*, file_name: str | None, file_bytes: bytes | None) -> str | None:
    if not file_name or not file_bytes:
        return None
    extension = Path(file_name).suffix.lower()
    if extension not in {".txt", ".md", ".csv"}:
        return None
    try:
        return file_bytes[:2000].decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes[:2000].decode("latin-1", errors="ignore")


def _role_ids(roles: dict[str, str], *role_codes: str) -> list[str]:
    return [roles[code] for code in role_codes if code in roles]
