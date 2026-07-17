from __future__ import annotations

from dataclasses import dataclass

from app.core.capabilities import (
    CAP_ANNOUNCEMENTS_WRITE,
    CAP_AUDIT_READ,
    CAP_DISCIPLINARY_TENANT_READ,
    CAP_DISCIPLINARY_WRITE,
    CAP_DOCUMENTS_WRITE,
    CAP_EVENTS_SPORTS_WRITE,
    CAP_FINANCE_AUDIT,
    CAP_FINANCE_SELF_READ,
    CAP_FINANCE_TENANT_READ,
    CAP_POLICIES_WRITE,
    CAP_TENANT_ADMINISTRATION,
)
from app.modules.tenancy.module_toggles import parse_module_toggles

DOMAIN_MEMBER_FINANCE = "member_finance"
DOMAIN_TENANT_FINANCE = "tenant_finance"
DOMAIN_GOVERNANCE = "governance"
DOMAIN_PUBLICATION = "publication"
DOMAIN_DISCIPLINARY = "disciplinary"
DOMAIN_SPORTS = "sports"


@dataclass(frozen=True)
class ChatDomainPolicy:
    member_finance: bool
    tenant_finance: bool
    governance: bool
    publication: bool
    disciplinary: bool
    sports: bool

    def allowed_domains(self) -> list[str]:
        domains: list[str] = []
        if self.member_finance:
            domains.append(DOMAIN_MEMBER_FINANCE)
        if self.tenant_finance:
            domains.append(DOMAIN_TENANT_FINANCE)
        if self.governance:
            domains.append(DOMAIN_GOVERNANCE)
        if self.publication:
            domains.append(DOMAIN_PUBLICATION)
        if self.disciplinary:
            domains.append(DOMAIN_DISCIPLINARY)
        if self.sports:
            domains.append(DOMAIN_SPORTS)
        return domains


def build_chat_domain_policy(
    *,
    capabilities: tuple[str, ...],
    tenant_settings_json: dict | None,
) -> ChatDomainPolicy:
    modules = parse_module_toggles(tenant_settings_json)
    membership_and_contributions = modules["membership"] and modules["contributions"]

    member_finance = CAP_FINANCE_SELF_READ in capabilities and membership_and_contributions
    tenant_finance = (
        any(
            capability in capabilities
            for capability in (
                CAP_FINANCE_TENANT_READ,
                CAP_FINANCE_AUDIT,
                CAP_TENANT_ADMINISTRATION,
            )
        )
        and membership_and_contributions
    )
    governance = any(
        capability in capabilities
        for capability in (
            CAP_FINANCE_TENANT_READ,
            CAP_FINANCE_AUDIT,
            CAP_AUDIT_READ,
            CAP_TENANT_ADMINISTRATION,
        )
    ) and any(
        (
            modules["membership"],
            modules["policies"],
            modules["announcements"],
            modules["events"],
        )
    )
    publication = any(
        capability in capabilities
        for capability in (
            CAP_DOCUMENTS_WRITE,
            CAP_POLICIES_WRITE,
            CAP_ANNOUNCEMENTS_WRITE,
            CAP_TENANT_ADMINISTRATION,
        )
    ) and any((modules["policies"], modules["announcements"]))
    disciplinary = any(
        capability in capabilities
        for capability in (
            CAP_DISCIPLINARY_TENANT_READ,
            CAP_DISCIPLINARY_WRITE,
            CAP_TENANT_ADMINISTRATION,
        )
    ) and modules["disciplinary"]
    sports = any(
        capability in capabilities
        for capability in (
            CAP_EVENTS_SPORTS_WRITE,
            CAP_TENANT_ADMINISTRATION,
        )
    ) and modules["events"]

    return ChatDomainPolicy(
        member_finance=member_finance,
        tenant_finance=tenant_finance,
        governance=governance,
        publication=publication,
        disciplinary=disciplinary,
        sports=sports,
    )
