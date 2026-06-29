from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

MODEL_MAP: dict[str, type] = {}


def _lazy_load_models() -> dict[str, type]:
    if MODEL_MAP:
        return MODEL_MAP
    from app.modules.announcements.models import Announcement
    from app.modules.chat.models import ChatQueryLog
    from app.modules.contributions.models import ContributionRecord
    from app.modules.disciplinary.models import DisciplinaryRecord
    from app.modules.events.models import Event
    from app.modules.membership.models import MembershipProfile
    from app.modules.notifications.models import NotificationChannel
    from app.modules.policies.models import PolicyRecord

    MODEL_MAP.update(
        {
            "membership": MembershipProfile,
            "contributions": ContributionRecord,
            "policies": PolicyRecord,
            "disciplinary": DisciplinaryRecord,
            "events": Event,
            "announcements": Announcement,
            "chat": ChatQueryLog,
            "notifications": NotificationChannel,
        }
    )
    return MODEL_MAP


async def module_has_data(db: AsyncSession, tenant_id: UUID, module: str) -> bool:
    """Return True when the tenant has any persisted records for a module."""
    models = _lazy_load_models()
    model = models.get(module)
    if model is None:
        return False

    result = await db.execute(
        select(func.count(model.id)).where(model.tenant_id == tenant_id)
    )
    return result.scalar_one() > 0
