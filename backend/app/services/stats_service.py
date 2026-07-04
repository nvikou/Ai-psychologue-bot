"""Service statistiques admin."""

from datetime import datetime
from datetime import timezone

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventLog
from app.models import Message
from app.models import PlanType
from app.models import User
from app.schemas import EventOut
from app.schemas import StatsOut
from app.schemas import UserOut


async def get_stats(db: AsyncSession) -> StatsOut:
    """Calcule les statistiques globales."""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    total_users = await db.scalar(select(func.count(User.id))) or 0
    total_messages = await db.scalar(
        select(func.count(Message.id))
    ) or 0

    active_today = await db.scalar(
        select(func.count(User.id)).where(
            User.last_active_at >= today_start
        )
    ) or 0

    messages_today = await db.scalar(
        select(func.count(Message.id)).where(
            Message.created_at >= today_start
        )
    ) or 0

    crisis_events_today = await db.scalar(
        select(func.count(EventLog.id)).where(
            EventLog.event_type == "crisis_detected",
            EventLog.created_at >= today_start,
        )
    ) or 0

    plan_rows = await db.execute(
        select(User.plan, func.count(User.id)).group_by(User.plan)
    )
    users_by_plan = {
        row[0].value: row[1] for row in plan_rows.all()
    }

    channel_rows = await db.execute(
        select(User.channel, func.count(User.id)).group_by(
            User.channel
        )
    )
    users_by_channel = {row[0]: row[1] for row in channel_rows.all()}

    return StatsOut(
        total_users=total_users,
        active_today=active_today,
        total_messages=total_messages,
        messages_today=messages_today,
        crisis_events_today=crisis_events_today,
        users_by_plan=users_by_plan,
        users_by_channel=users_by_channel,
    )


async def list_users(
    db: AsyncSession,
    limit: int = 50,
) -> list[UserOut]:
    """Liste les utilisateurs avec compteur de messages."""
    result = await db.execute(
        select(User).order_by(User.last_active_at.desc()).limit(limit)
    )
    users = result.scalars().all()
    output: list[UserOut] = []
    for user in users:
        count = await db.scalar(
            select(func.count(Message.id)).where(
                Message.user_id == user.id
            )
        ) or 0
        output.append(
            UserOut(
                id=user.id,
                external_id=user.external_id,
                channel=user.channel,
                username=user.username,
                first_name=user.first_name,
                plan=user.plan,
                message_count=count,
                created_at=user.created_at,
                last_active_at=user.last_active_at,
            )
        )
    return output


async def list_recent_events(
    db: AsyncSession,
    limit: int = 30,
) -> list[EventOut]:
    """Liste les événements récents."""
    result = await db.execute(
        select(EventLog)
        .order_by(EventLog.created_at.desc())
        .limit(limit)
    )
    return [EventOut.model_validate(e) for e in result.scalars()]


async def update_user_plan(
    db: AsyncSession,
    user_id: int,
    plan: PlanType,
) -> User | None:
    """Met à jour le plan d'abonnement."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    user.plan = plan
    return user
