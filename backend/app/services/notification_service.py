"""Service notifications (préférences utilisateur)."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User

logger = logging.getLogger(__name__)


async def list_users_for_checkin(
    db: AsyncSession,
) -> list[User]:
    """Utilisateurs ayant activé les notifications."""
    result = await db.execute(
        select(User).where(User.notify_enabled.is_(True))
    )
    users = list(result.scalars().all())
    logger.info("checkin candidates=%s", len(users))
    return users
