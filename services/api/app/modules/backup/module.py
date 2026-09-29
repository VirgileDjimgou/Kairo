from __future__ import annotations

from app.core.capabilities import (
    CAP_BACKUP_CREATE,
    CAP_BACKUP_READ,
    CAP_BACKUP_RESTORE_REQUEST,
)
from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="backup",
    name="Recovery centre",
    description="Encrypted backups, restore drills and recovery evidence.",
    capabilities=(CAP_BACKUP_CREATE, CAP_BACKUP_READ, CAP_BACKUP_RESTORE_REQUEST),
    router_module="app.modules.backup.router",
    router_order=60,
)
