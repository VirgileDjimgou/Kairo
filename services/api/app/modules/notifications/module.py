from __future__ import annotations

from app.core.capabilities import CAP_TENANT_ADMINISTRATION
from app.modules.domain_events.events import (
    RECEIPT_DECLARED,
    RECEIPT_HANDOVER_REMINDER_UPDATED,
    RECEIPT_HANDOVER_REPORTED,
    RECEIPT_RECEIVED_IN_TREASURY,
    receipt_processed_event_type,
)
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

_PROCESSED_EVENT_TYPES = tuple(
    receipt_processed_event_type(action)
    for action in (
        "validated",
        "partially_validated",
        "rejected",
        "clarification_requested",
        "cancelled",
    )
)

MODULE = ModuleDescriptor(
    key="notifications",
    name="Notifications",
    description="Authenticated inbox, preferences, devices, Web Push and Android FCM delivery hints.",
    capabilities=(CAP_TENANT_ADMINISTRATION,),
    tenant_toggle=True,
    toggle_order=80,
    router_module="app.modules.notifications.router",
    router_attrs=("router", "callback_router"),
    router_order=160,
    domain_event_types=(
        RECEIPT_DECLARED,
        *_PROCESSED_EVENT_TYPES,
        RECEIPT_HANDOVER_REPORTED,
        RECEIPT_HANDOVER_REMINDER_UPDATED,
        RECEIPT_RECEIVED_IN_TREASURY,
    ),
    navigation=(
        NavigationEntry(
            key="notifications",
            label_key="nav.notifications",
            path="/notifications",
            section="member",
            order=70,
        ),
    ),
)
