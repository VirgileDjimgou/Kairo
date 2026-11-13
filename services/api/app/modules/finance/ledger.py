"""Ledger derivation rules shared by every finance mixin."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.modules.contributions.models import ContributionStatus

CENT = Decimal("0.01")


def as_decimal(value: object) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT)


def as_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def derive_contribution_status(
    *,
    expected: Decimal,
    paid: Decimal,
    due_date: datetime | None,
    waived: bool,
) -> str:
    """Single source of truth for ``ContributionRecord.status``.

    ``waived`` is an administrative decision and always wins. Every other status
    is derived from the amount actually paid, never supplied by a client.
    """
    if waived:
        return ContributionStatus.waived.value
    if expected > 0 and paid >= expected:
        return ContributionStatus.paid.value
    if paid > 0:
        return ContributionStatus.partial.value
    due = as_aware(due_date)
    if due is not None and due < datetime.now(UTC):
        return ContributionStatus.overdue.value
    return ContributionStatus.pending.value
