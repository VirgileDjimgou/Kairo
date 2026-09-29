from __future__ import annotations

from pydantic import BaseModel


class ModuleNavigationEntryResponse(BaseModel):
    key: str
    label_key: str
    path: str
    section: str
    order: int
    capabilities: list[str]


class RegisteredModuleResponse(BaseModel):
    key: str
    name: str
    description: str
    enabled: bool
    capabilities: list[str]
    depends_on: list[str]
    domain_event_types: list[str]
    navigation: list[ModuleNavigationEntryResponse]


class RegisteredModulesResponse(BaseModel):
    modules: list[RegisteredModuleResponse]
