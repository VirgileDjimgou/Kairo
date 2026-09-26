from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SearchType = Literal[
    "members",
    "documents",
    "events",
    "announcements",
    "payments",
    "receipts",
    "audit",
    "discipline",
]


class SearchResult(BaseModel):
    id: str
    type: SearchType
    type_key: str = Field(description="Localization key for the type label, e.g. search.types.members")
    title: str
    subtitle: str | None = None
    target_path: str = Field(description="Safe internal destination")
    score: int = Field(ge=0, description="3 exact, 2 prefix, 1 substring match")


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
