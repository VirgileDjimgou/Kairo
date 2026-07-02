from collections.abc import Iterable

CAP_TENANT_ADMINISTRATION = "tenant:administration"
CAP_TENANT_SETTINGS_WRITE = "tenant:settings_write"
CAP_ROLE_CATALOG_READ = "roles:read_catalog"
CAP_ROLE_ASSIGN = "roles:assign"
CAP_AUDIT_READ = "audit:read"
CAP_MEMBERSHIP_SELF_READ = "membership:self_read"
CAP_MEMBERSHIP_TENANT_READ = "membership:tenant_read"
CAP_MEMBERSHIP_WRITE = "membership:write"
CAP_FINANCE_SELF_READ = "finance:self_read"
CAP_FINANCE_TENANT_READ = "finance:tenant_read"
CAP_FINANCE_WRITE = "finance:write"
CAP_FINANCE_AUDIT = "finance:audit"
CAP_DOCUMENTS_READ = "documents:read"
CAP_DOCUMENTS_WRITE = "documents:write"
CAP_POLICIES_READ = "policies:read"
CAP_POLICIES_WRITE = "policies:write"
CAP_DISCIPLINARY_SELF_READ = "disciplinary:self_read"
CAP_DISCIPLINARY_TENANT_READ = "disciplinary:tenant_read"
CAP_DISCIPLINARY_WRITE = "disciplinary:write"
CAP_EVENTS_READ = "events:read"
CAP_EVENTS_WRITE = "events:write"
CAP_EVENTS_SPORTS_WRITE = "events:sports_write"
CAP_ANNOUNCEMENTS_READ = "announcements:read"
CAP_ANNOUNCEMENTS_WRITE = "announcements:write"
CAP_CHAT_USE = "chat:use"
CAP_EXPORT_SENSITIVE = "exports:sensitive"

CAPABILITY_ORDER = (
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
    CAP_EVENTS_SPORTS_WRITE,
    CAP_ANNOUNCEMENTS_READ,
    CAP_ANNOUNCEMENTS_WRITE,
    CAP_CHAT_USE,
    CAP_EXPORT_SENSITIVE,
)


def _ordered_capabilities(capabilities: Iterable[str]) -> tuple[str, ...]:
    capability_set = set(capabilities)
    return tuple(cap for cap in CAPABILITY_ORDER if cap in capability_set)


LEGACY_ROLE_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "admin": tuple(CAPABILITY_ORDER),
}


def has_capability(role_codes: Iterable[str], capability: str) -> bool:
    return capability in capabilities_for_roles(role_codes)


def capabilities_for_roles(role_codes: Iterable[str]) -> tuple[str, ...]:
    from app.modules.tenancy.role_catalog import get_role_definition

    aggregated: set[str] = set()
    for code in role_codes:
        definition = get_role_definition(code)
        if definition is not None:
            aggregated.update(definition.capabilities)
        aggregated.update(LEGACY_ROLE_CAPABILITIES.get(code, ()))
    return _ordered_capabilities(aggregated)
