"""RGPD : suppression compte et rétention des messages."""

import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import EventLog
from app.models import Message
from app.models import User

logger = logging.getLogger(__name__)


async def delete_user_data(
    db: AsyncSession,
    external_id: str,
) -> bool:
    """Supprime un utilisateur et toutes ses données (droit à l'oubli)."""
    result = await db.execute(
        select(User).where(User.external_id == external_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return False
    await db.execute(
        delete(EventLog).where(EventLog.user_id == user.id)
    )
    await db.execute(
        delete(Message).where(Message.user_id == user.id)
    )
    await db.delete(user)
    logger.info("GDPR delete completed for external_id=%s", external_id)
    return True


async def purge_expired_messages(db: AsyncSession) -> int:
    """Supprime les messages plus vieux que message_retention_days."""
    cutoff = datetime.now(timezone.utc) - timedelta(
        days=settings.message_retention_days
    )
    result = await db.execute(
        delete(Message).where(Message.created_at < cutoff)
    )
    deleted = result.rowcount or 0
    logger.info(
        "Retention purge deleted=%s older_than_days=%s",
        deleted,
        settings.message_retention_days,
    )
    return deleted


async def export_user_data(
    db: AsyncSession,
    external_id: str,
) -> dict | None:
    """Exporte les données utilisateur (portabilité RGPD)."""
    from app.services.encryption_service import decrypt_text

    result = await db.execute(
        select(User).where(User.external_id == external_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    messages_result = await db.execute(
        select(Message)
        .where(Message.user_id == user.id)
        .order_by(Message.created_at.asc())
    )
    messages = [
        {
            "role": m.role,
            "content": decrypt_text(m.content, m.is_encrypted),
            "is_crisis": m.is_crisis,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages_result.scalars().all()
    ]
    return {
        "external_id": user.external_id,
        "channel": user.channel,
        "username": user.username,
        "first_name": user.first_name,
        "language": user.language,
        "goals": user.goals,
        "timezone": user.timezone,
        "plan": user.plan.value,
        "created_at": user.created_at.isoformat(),
        "messages": messages,
    }
