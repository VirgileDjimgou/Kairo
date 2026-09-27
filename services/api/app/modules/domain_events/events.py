from __future__ import annotations

from typing import Final

AGGREGATE_RECEIPT_DECLARATION: Final = "contribution_receipt_declaration"
MODULE_CONTRIBUTIONS: Final = "contributions"

RECEIPT_DECLARED: Final = "finance.receipt_declared"
RECEIPT_UPDATED: Final = "finance.receipt_updated"
RECEIPT_SUBMITTED: Final = "finance.receipt_submitted"
RECEIPT_HANDOVER_REPORTED: Final = "finance.receipt_handover_reported"
RECEIPT_HANDOVER_REMINDER_UPDATED: Final = "finance.receipt_handover_reminder_updated"
RECEIPT_RECEIVED_IN_TREASURY: Final = "finance.receipt_received_in_treasury"

PAYMENT_RECORDED: Final = "finance.payment_recorded"
EXPENSE_RECORDED: Final = "finance.expense_recorded"

AGGREGATE_PAYMENT: Final = "payment_record"
AGGREGATE_EXPENSE: Final = "expense_record"

RECEIPT_PROCESSED_ACTIONS: Final = frozenset(
    {
        "validated",
        "partially_validated",
        "rejected",
        "clarification_requested",
        "cancelled",
    }
)

RECEIPT_PROCESSED_EVENT_TYPES: Final = frozenset(
    f"finance.receipt_{action}" for action in RECEIPT_PROCESSED_ACTIONS
)

RECEIPT_LIFECYCLE_EVENT_TYPES: Final = frozenset(
    {
        RECEIPT_DECLARED,
        RECEIPT_UPDATED,
        RECEIPT_SUBMITTED,
        RECEIPT_HANDOVER_REPORTED,
        RECEIPT_HANDOVER_REMINDER_UPDATED,
        RECEIPT_RECEIVED_IN_TREASURY,
    }
) | RECEIPT_PROCESSED_EVENT_TYPES


def receipt_processed_event_type(action: str) -> str:
    return f"finance.receipt_{action}"
