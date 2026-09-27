from __future__ import annotations

import re

PERSONAL_FINANCE_SELF_PATTERNS = (
    r"\bmy balance\b",
    r"\bmy dues\b",
    r"\bmy contribution(?:s)?\b",
    r"\bwhat do i owe\b",
    r"\bhow much do i owe\b",
    r"\bwhat is my balance\b",
    r"\bwhat is owing\b",
    r"\bmy statement\b",
    r"\b(mon|mes)\b.*\b(solde|cotisation(?:s)?|contribution(?:s)?|reste|paiement(?:s)?)\b",
    r"\bquelle est ma\b.*\b(cotisation|contribution)\b",
    r"\bquel est mon\b.*\b(solde|reste)\b",
    r"\b(mein|meine)\b.*\b(saldo|beitrag|beitraege|restbetrag|zahlung(?:en)?)\b",
    r"\bwie hoch ist mein\b.*\b(saldo|beitrag|restbetrag)\b",
)

TENANT_FINANCE_PATTERNS = (
    r"\btenant summary\b",
    r"\bfinance summary\b",
    r"\bcontribution summary\b",
    r"\bcollection rate\b",
    r"\btotal balance\b",
    r"\btotal paid\b",
    r"\btotal expected\b",
    r"\boutstanding balance\b",
    r"\bfinance report\b",
    r"\bhow many contributions\b",
    r"\bhow many members have paid\b",
    r"\br[ée]sum[ée] financier\b",
    r"\bsynth[èe]se des cotisations\b",
    r"\btaux de recouvrement\b",
    r"\bsolde total\b",
    r"\btotal pay[ée]\b",
    r"\btotal attendu\b",
    r"\bzusammenfassung der finanzen\b",
    r"\bfinanz(?:en)?zusammenfassung\b",
    r"\beinziehungsquote\b",
    r"\bgesamtsaldo\b",
    r"\bgesamt bezahlt\b",
    r"\bgesamt erwartet\b",
)

OTHER_MEMBER_FINANCE_PATTERNS = (
    r"\banother member\b.*\b(balance|dues|fee|fees|contribution|contributions|owed|owing)\b",
    r"\b(other|another|their|his|her)\b.*\b(balance|dues|fee|fees|contribution|contributions|owed|owing)\b",
    r"\b(balance|dues|fee|fees|contribution|contributions|owed|owing)\b.*\b(of|for)\b.*\b(member|user|profile)\b",
    r"\b(son|sa|ses|leur|leurs)\b.*\b(solde|cotisation(?:s)?|contribution(?:s)?|reste)\b",
    r"\b(solde|cotisation(?:s)?|contribution(?:s)?|reste)\b.*\b(d['e]|de|du|des|pour)\b.*\b(un autre membre|autre membre|membre|adh[ée]rent)\b",
    r"\b(solde|cotisation(?:s)?|contribution(?:s)?|reste)\b.*\b(d['e]|de|du|des|pour)\b\s+[a-zà-ÿ'-]+(?:\s+[a-zà-ÿ'-]+){1,2}\b",
    r"\b(sein|seine|seiner|ihre|ihr|deren)\b.*\b(saldo|beitrag|beitraege|restbetrag)\b",
    r"\b(saldo|beitrag|beitraege|restbetrag)\b.*\b(von|fuer|für)\b.*\b(einem anderen mitglied|anderen mitglied|mitglied)\b",
    r"\b(saldo|beitrag|beitraege|restbetrag)\b.*\b(von|fuer|für)\b\s+[a-zà-ÿ'-]+(?:\s+[a-zà-ÿ'-]+){1,2}\b",
)

FINANCE_TOPIC_PATTERNS = (
    r"\bbalance\b",
    r"\bdues\b",
    r"\bfee(?:s)?\b",
    r"\bcontribution(?:s)?\b",
    r"\bowed\b",
    r"\bowing\b",
    r"\bsolde\b",
    r"\bcotisation(?:s)?\b",
    r"\breste\b",
    r"\bcontribution(?:s)?\b",
    r"\bsaldo\b",
    r"\bbeitrag\b",
    r"\bbeitraege\b",
    r"\brestbetrag\b",
)

GOVERNANCE_SUMMARY_PATTERNS = (
    r"\bgovernance summary\b",
    r"\borganization summary\b",
    r"\borganization overview\b",
    r"\btenant overview\b",
    r"\bexecutive overview\b",
    r"\bboard overview\b",
    r"\bmember directory overview\b",
    r"\bmember count\b",
    r"\bdocument count\b",
    r"\bannouncement count\b",
    r"\bevent count\b",
    r"\bpolicy count\b",
    r"\br[ée]sum[ée] de gouvernance\b",
    r"\baper[çc]u de l'organisation\b",
    r"\baper[çc]u du tenant\b",
    r"\bnombre de membres\b",
    r"\bgovernance-zusammenfassung\b",
    r"\bvereinsueberblick\b",
    r"\btenant-ueberblick\b",
    r"\banzahl der mitglieder\b",
)

PUBLICATION_CONTEXT_PATTERNS = (
    r"\bpublication context\b",
    r"\bofficial publication\b",
    r"\bofficial publications\b",
    r"\bpublication status\b",
    r"\bannouncement status\b",
    r"\bwhat should i publish\b",
    r"\bwhat needs to be published\b",
    r"\bofficial notices\b",
    r"\bcontexte de publication\b",
    r"\bcontexte officiel de publication\b",
    r"\bpublication officielle\b",
    r"\bquelles annonces sont actives\b",
    r"\bquels documents sont pr[êe]ts [àa] [êe]tre publi[ée]s\b",
    r"\bpublikationskontext\b",
    r"\boffizielle veroeffentlichung\b",
    r"\bwelche ankuendigungen sind aktiv\b",
    r"\bwelche dokumente sind zur veroeffentlichung bereit\b",
)

DISCIPLINARY_SUMMARY_PATTERNS = (
    r"\bdisciplinary summary\b",
    r"\bsanctions overview\b",
    r"\bcompliance overview\b",
    r"\bopen cases\b",
    r"\bcase summary\b",
    r"\br[ée]sum[ée] disciplinaire\b",
    r"\baper[çc]u des sanctions\b",
    r"\bcombien de dossiers sont ouverts\b",
    r"\bdisziplinarische zusammenfassung\b",
    r"\bsanktionsuebersicht\b",
    r"\bwieviele faelle sind offen\b",
)

SPORTS_SCHEDULE_PATTERNS = (
    r"\bsports schedule\b",
    r"\bsports calendar\b",
    r"\btraining schedule\b",
    r"\bfixture schedule\b",
    r"\bupcoming sports events\b",
    r"\bnext sports event\b",
    r"\bsports plan\b",
    r"\bcalendrier sportif\b",
    r"\bprochain [ée]v[ée]nement sportif\b",
    r"\bwelcher sportkalender\b",
    r"\bnaechste sportveranstaltung\b",
    r"\bsportkalender\b",
)


def question_mentions_any(question: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, question) for pattern in patterns)


def question_mentions_personal_finance(question: str) -> bool:
    return question_mentions_any(question, PERSONAL_FINANCE_SELF_PATTERNS)


def question_mentions_tenant_finance(question: str) -> bool:
    return question_mentions_any(question, TENANT_FINANCE_PATTERNS)


def question_mentions_finance_topic(question: str) -> bool:
    return question_mentions_any(question, FINANCE_TOPIC_PATTERNS)


def question_mentions_named_target(question: str) -> bool:
    return any(
        re.search(pattern, question)
        for pattern in (
            r"\b(of|for|de|du|des|pour|von|fuer|für)\b\s+[a-zà-ÿ'-]+(?:\s+[a-zà-ÿ'-]+){1,2}\b",
            r"\b(other|another|their|his|her|son|sa|ses|leur|leurs|sein|seine|ihr|ihre)\b",
        )
    )


def question_mentions_other_member_finance(question: str) -> bool:
    if question_mentions_any(question, OTHER_MEMBER_FINANCE_PATTERNS):
        return True
    return (
        question_mentions_finance_topic(question)
        and not question_mentions_personal_finance(question)
        and not question_mentions_tenant_finance(question)
        and question_mentions_named_target(question)
    )
