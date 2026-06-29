# Import all ORM models here so that Base.metadata is fully populated.
# This file must be imported before any call to Base.metadata.create_all()
# or alembic autogenerate.

from app.modules.identity.models import (  # noqa: F401
    Invitation,
    PasswordResetToken,
    User,
    UserSession,
)
from app.modules.documents.models import (  # noqa: F401
    Document,
    DocumentChunk,
    DocumentVersion,
    IngestionJob,
)
from app.modules.chat.models import ChatQueryLog  # noqa: F401
from app.modules.audit.models import AuditEvent  # noqa: F401
from app.modules.tenancy.models import (  # noqa: F401
    Permission,
    Role,
    RolePermission,
    Tenant,
    TenantUser,
    UserRole,
)
from app.modules.membership.models import MembershipProfile  # noqa: F401
from app.modules.contributions.models import (  # noqa: F401
    ContributionRecord,
    PaymentRecord,
)
from app.modules.policies.models import PolicyRecord  # noqa: F401
from app.modules.disciplinary.models import DisciplinaryRecord  # noqa: F401
from app.modules.events.models import Event  # noqa: F401
from app.modules.announcements.models import Announcement  # noqa: F401
