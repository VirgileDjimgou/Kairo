from __future__ import annotations

from app.core.capabilities import (
    CAP_CONTRIBUTION_RECEIPT_DECLARE,
    CAP_CONTRIBUTION_RECEIPT_MEMBER_SELF_READ,
    CAP_CONTRIBUTION_RECEIPT_OWN_READ,
    CAP_CONTRIBUTION_RECEIPT_PROCESS,
    CAP_CONTRIBUTION_RECEIPT_TENANT_READ,
    CAP_EXPORT_SENSITIVE,
    CAP_FINANCE_AUDIT,
    CAP_FINANCE_EXPENSES_WRITE,
    CAP_FINANCE_SELF_READ,
    CAP_FINANCE_TENANT_READ,
    CAP_FINANCE_WRITE,
)
from app.modules.domain_events.events import EXPENSE_RECORDED, PAYMENT_RECORDED
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

MODULE = ModuleDescriptor(
    key="contributions",
    name="Contributions and finance",
    description="Contributions, payments, receipts, custody, expenses, budgets and exports.",
    capabilities=(
        CAP_FINANCE_SELF_READ,
        CAP_FINANCE_TENANT_READ,
        CAP_FINANCE_WRITE,
        CAP_FINANCE_EXPENSES_WRITE,
        CAP_FINANCE_AUDIT,
        CAP_EXPORT_SENSITIVE,
        CAP_CONTRIBUTION_RECEIPT_DECLARE,
        CAP_CONTRIBUTION_RECEIPT_OWN_READ,
        CAP_CONTRIBUTION_RECEIPT_MEMBER_SELF_READ,
        CAP_CONTRIBUTION_RECEIPT_TENANT_READ,
        CAP_CONTRIBUTION_RECEIPT_PROCESS,
    ),
    tenant_toggle=True,
    toggle_order=20,
    router_module="app.modules.contributions.router",
    router_order=100,
    search_order=50,
    search_providers=(
        ("app.modules.search.providers", "PaymentsSearchProvider"),
        ("app.modules.search.providers", "ReceiptsSearchProvider"),
    ),
    domain_event_types=(PAYMENT_RECORDED, EXPENSE_RECORDED),
    navigation=(
        NavigationEntry(
            key="finance",
            label_key="nav.financeWorkspace",
            path="/finance",
            section="office",
            order=20,
            capabilities=(CAP_FINANCE_SELF_READ,),
        ),
    ),
)
