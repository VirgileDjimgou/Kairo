from dataclasses import dataclass

from app.core.capabilities import (
    CAP_ANNOUNCEMENTS_READ,
    CAP_ANNOUNCEMENTS_WRITE,
    CAP_AUDIT_READ,
    CAP_CHAT_USE,
    CAP_DISCIPLINARY_SELF_READ,
    CAP_DISCIPLINARY_TENANT_READ,
    CAP_DISCIPLINARY_WRITE,
    CAP_DOCUMENTS_READ,
    CAP_DOCUMENTS_WRITE,
    CAP_EVENTS_READ,
    CAP_EVENTS_WRITE,
    CAP_EVENTS_SPORTS_WRITE,
    CAP_EXPORT_SENSITIVE,
    CAP_FINANCE_AUDIT,
    CAP_FINANCE_SELF_READ,
    CAP_FINANCE_TENANT_READ,
    CAP_FINANCE_WRITE,
    CAP_MEMBERSHIP_SELF_READ,
    CAP_MEMBERSHIP_TENANT_READ,
    CAP_MEMBERSHIP_WRITE,
    CAP_POLICIES_READ,
    CAP_POLICIES_WRITE,
    CAP_ROLE_ASSIGN,
    CAP_ROLE_CATALOG_READ,
    CAP_TENANT_ADMINISTRATION,
    CAP_TENANT_SETTINGS_WRITE,
)


@dataclass(frozen=True)
class RoleDefinition:
    code: str
    name: str
    description: str
    capabilities: tuple[str, ...]
    profile_type: str = "member"
    is_system_role: bool = True


ROLE_DEFINITIONS: tuple[RoleDefinition, ...] = (
    RoleDefinition(
        code="principal_admin",
        name="Principal Administrator",
        description="Tenant-wide operator with the broadest governance and administrative authority.",
        capabilities=(
            CAP_TENANT_ADMINISTRATION,
            CAP_TENANT_SETTINGS_WRITE,
            CAP_ROLE_CATALOG_READ,
            CAP_ROLE_ASSIGN,
            CAP_AUDIT_READ,
            CAP_MEMBERSHIP_SELF_READ,
            CAP_MEMBERSHIP_TENANT_READ,
            CAP_MEMBERSHIP_WRITE,
            CAP_FINANCE_SELF_READ,
            CAP_FINANCE_TENANT_READ,
            CAP_FINANCE_WRITE,
            CAP_FINANCE_AUDIT,
            CAP_DOCUMENTS_READ,
            CAP_DOCUMENTS_WRITE,
            CAP_POLICIES_READ,
            CAP_POLICIES_WRITE,
            CAP_DISCIPLINARY_SELF_READ,
            CAP_DISCIPLINARY_TENANT_READ,
            CAP_DISCIPLINARY_WRITE,
            CAP_EVENTS_READ,
            CAP_EVENTS_WRITE,
            CAP_ANNOUNCEMENTS_READ,
            CAP_ANNOUNCEMENTS_WRITE,
            CAP_CHAT_USE,
            CAP_EXPORT_SENSITIVE,
        ),
        profile_type="admin",
    ),
    RoleDefinition(
        code="president",
        name="President",
        description="Executive oversight role with cross-domain read access and governance visibility.",
        capabilities=(
            CAP_ROLE_CATALOG_READ,
            CAP_AUDIT_READ,
            CAP_MEMBERSHIP_SELF_READ,
            CAP_MEMBERSHIP_TENANT_READ,
            CAP_FINANCE_SELF_READ,
            CAP_FINANCE_TENANT_READ,
            CAP_FINANCE_AUDIT,
            CAP_DOCUMENTS_READ,
            CAP_POLICIES_READ,
            CAP_DISCIPLINARY_TENANT_READ,
            CAP_EVENTS_READ,
            CAP_ANNOUNCEMENTS_READ,
            CAP_CHAT_USE,
        ),
        profile_type="staff",
    ),
    RoleDefinition(
        code="vice_president",
        name="Vice President",
        description="Deputy executive with broad visibility but narrower oversight than the president.",
        capabilities=(
            CAP_ROLE_CATALOG_READ,
            CAP_MEMBERSHIP_SELF_READ,
            CAP_MEMBERSHIP_TENANT_READ,
            CAP_FINANCE_SELF_READ,
            CAP_FINANCE_TENANT_READ,
            CAP_DOCUMENTS_READ,
            CAP_POLICIES_READ,
            CAP_EVENTS_READ,
            CAP_ANNOUNCEMENTS_READ,
            CAP_CHAT_USE,
        ),
        profile_type="staff",
    ),
    RoleDefinition(
        code="secretary_general",
        name="Secretary General",
        description="Office role responsible for governance documents, announcements, and formal records.",
        capabilities=(
            CAP_MEMBERSHIP_SELF_READ,
            CAP_MEMBERSHIP_TENANT_READ,
            CAP_DOCUMENTS_READ,
            CAP_DOCUMENTS_WRITE,
            CAP_POLICIES_READ,
            CAP_POLICIES_WRITE,
            CAP_EVENTS_READ,
            CAP_ANNOUNCEMENTS_READ,
            CAP_ANNOUNCEMENTS_WRITE,
            CAP_CHAT_USE,
        ),
        profile_type="staff",
    ),
    RoleDefinition(
        code="treasurer",
        name="Treasurer",
        description="Finance operations role for contribution management and payment recording.",
        capabilities=(
            CAP_MEMBERSHIP_SELF_READ,
            CAP_MEMBERSHIP_TENANT_READ,
            CAP_FINANCE_SELF_READ,
            CAP_FINANCE_TENANT_READ,
            CAP_FINANCE_WRITE,
            CAP_DOCUMENTS_READ,
            CAP_EVENTS_READ,
            CAP_ANNOUNCEMENTS_READ,
            CAP_CHAT_USE,
        ),
        profile_type="staff",
    ),
    RoleDefinition(
        code="auditor",
        name="Auditor",
        description="Read-only finance and governance oversight role for internal controls.",
        capabilities=(
            CAP_ROLE_CATALOG_READ,
            CAP_AUDIT_READ,
            CAP_MEMBERSHIP_SELF_READ,
            CAP_MEMBERSHIP_TENANT_READ,
            CAP_FINANCE_SELF_READ,
            CAP_FINANCE_TENANT_READ,
            CAP_FINANCE_AUDIT,
            CAP_DOCUMENTS_READ,
            CAP_POLICIES_READ,
            CAP_EVENTS_READ,
            CAP_ANNOUNCEMENTS_READ,
            CAP_CHAT_USE,
            CAP_EXPORT_SENSITIVE,
        ),
        profile_type="staff",
    ),
    RoleDefinition(
        code="censor",
        name="Censor",
        description="Disciplinary governance role for sanctions, compliance, and private record stewardship.",
        capabilities=(
            CAP_MEMBERSHIP_SELF_READ,
            CAP_MEMBERSHIP_TENANT_READ,
            CAP_DISCIPLINARY_SELF_READ,
            CAP_DISCIPLINARY_TENANT_READ,
            CAP_DISCIPLINARY_WRITE,
            CAP_DOCUMENTS_READ,
            CAP_POLICIES_READ,
            CAP_CHAT_USE,
        ),
        profile_type="staff",
    ),
    RoleDefinition(
        code="sports_manager",
        name="Sports Manager",
        description="Delegated operator for sports programming and event coordination.",
        capabilities=(
            CAP_MEMBERSHIP_SELF_READ,
            CAP_EVENTS_READ,
            CAP_EVENTS_SPORTS_WRITE,
            CAP_ANNOUNCEMENTS_READ,
            CAP_CHAT_USE,
        ),
        profile_type="staff",
    ),
    RoleDefinition(
        code="member",
        name="Member",
        description="Ordinary association member with a simple self-service and read-only experience.",
        capabilities=(
            CAP_MEMBERSHIP_SELF_READ,
            CAP_FINANCE_SELF_READ,
            CAP_DOCUMENTS_READ,
            CAP_POLICIES_READ,
            CAP_DISCIPLINARY_SELF_READ,
            CAP_EVENTS_READ,
            CAP_ANNOUNCEMENTS_READ,
            CAP_CHAT_USE,
        ),
        profile_type="member",
    ),
)

ROLE_DEFINITIONS_BY_CODE = {definition.code: definition for definition in ROLE_DEFINITIONS}
CANONICAL_ROLE_CODES = frozenset(ROLE_DEFINITIONS_BY_CODE)


def get_role_definition(code: str) -> RoleDefinition | None:
    return ROLE_DEFINITIONS_BY_CODE.get(code)


def canonical_role_definitions() -> tuple[RoleDefinition, ...]:
    return ROLE_DEFINITIONS


def is_canonical_role(code: str) -> bool:
    return code in CANONICAL_ROLE_CODES
