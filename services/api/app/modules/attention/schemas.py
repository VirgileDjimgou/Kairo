from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AttentionPriority = Literal["urgent", "attention", "normal", "informational"]
AttentionCategory = Literal["finance", "governance", "community", "account", "knowledge"]


class AttentionItem(BaseModel):
    """One backend-authorized attention card for the action center.

    ``title_key`` is a localization key owned by the clients; ``count`` is only
    ever computed from records the requesting role is already allowed to read.
    """

    id: str = Field(description="Stable item key, e.g. attention.pendingReceipts")
    priority: AttentionPriority
    category: AttentionCategory
    title_key: str
    count: int = Field(ge=0)
    target_path: str = Field(description="Safe internal destination for the action")


class AttentionOverview(BaseModel):
    items: list[AttentionItem]
