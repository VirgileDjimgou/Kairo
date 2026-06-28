# Import all ORM models here so that Base.metadata is fully populated.
# This file must be imported before any call to Base.metadata.create_all()
# or alembic autogenerate.

from app.modules.identity.models import User  # noqa: F401
from app.modules.documents.models import (  # noqa: F401
    Document,
    DocumentChunk,
    DocumentVersion,
    IngestionJob,
)
from app.modules.chat.models import ChatQueryLog  # noqa: F401
from app.modules.tenancy.models import (  # noqa: F401
    Permission,
    Role,
    RolePermission,
    Tenant,
    TenantUser,
    UserRole,
)
