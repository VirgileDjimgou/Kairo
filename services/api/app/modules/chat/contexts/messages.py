from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    "other_member_finance_forbidden": {
        "fr": "Les demandes concernant les finances personnelles d'un autre membre ne sont pas autorisées.",
        "en": "Requests for another member's personal finance data are not allowed.",
        "de": "Anfragen zu den persoenlichen Finanzdaten eines anderen Mitglieds sind nicht erlaubt.",
    },
    "personal_finance_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux soldes personnels via le chat.",
        "en": "Your role cannot access personal contribution balances through chat.",
        "de": "Ihre Rolle darf persoenliche Beitragssalden nicht per Chat abrufen.",
    },
    "tenant_finance_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux synthèses financières globales via le chat.",
        "en": "Your role cannot access tenant-wide finance summaries through chat.",
        "de": "Ihre Rolle darf keine tenant-weiten Finanzzusammenfassungen per Chat abrufen.",
    },
    "no_authorized_answer": {
        "fr": "Je n'ai pas trouvé de réponse fiable dans les documents autorisés ni dans les données structurées auxquelles vous avez accès.",
        "en": "I could not find a reliable answer in the authorized documents or structured data available to you.",
        "de": "Ich konnte in den freigegebenen Dokumenten oder strukturierten Daten, auf die Sie zugreifen duerfen, keine verlaessliche Antwort finden.",
    },
    "no_authorized_source": {
        "fr": "Aucune source autorisée ne correspond à la question.",
        "en": "No authorized source matched the question.",
        "de": "Keine autorisierte Quelle passte zur Frage.",
    },
    "governance_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux synthèses de gouvernance via le chat.",
        "en": "Your role cannot access governance summaries through chat.",
        "de": "Ihre Rolle darf keine Governance-Zusammenfassungen per Chat abrufen.",
    },
    "publication_forbidden": {
        "fr": "Votre rôle ne peut pas accéder au contexte de publication via le chat.",
        "en": "Your role cannot access publication context through chat.",
        "de": "Ihre Rolle darf nicht auf den Publikationskontext per Chat zugreifen.",
    },
    "disciplinary_forbidden": {
        "fr": "Votre rôle ne peut pas accéder aux synthèses disciplinaires via le chat.",
        "en": "Your role cannot access disciplinary summaries through chat.",
        "de": "Ihre Rolle darf keine disziplinarischen Zusammenfassungen per Chat abrufen.",
    },
    "sports_forbidden": {
        "fr": "Votre rôle ne peut pas accéder au calendrier sportif via le chat.",
        "en": "Your role cannot access sports schedules through chat.",
        "de": "Ihre Rolle darf nicht auf Sportkalender per Chat zugreifen.",
    },
}


def message(key: str, language: str) -> str:
    translations = MESSAGES[key]
    return translations.get(language, translations["en"])
