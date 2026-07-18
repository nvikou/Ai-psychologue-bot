"""Logique métier : utilisateurs, conversations, chat."""

import logging
from datetime import datetime
from datetime import timezone

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import EventLog
from app.models import Message
from app.models import PlanType
from app.models import User
from app.schemas import ChatRequest
from app.schemas import ChatResponse
from app.services.crisis_notify import notify_crisis
from app.services.crisis_service import is_crisis_message
from app.services.encryption_service import decrypt_text
from app.services.encryption_service import encrypt_text
from app.services.i18n_service import crisis_text
from app.services.i18n_service import normalize_language
from app.services.openai_service import AIServiceError
from app.services.openai_service import generate_reply
from app.services.quota_service import QuotaService

logger = logging.getLogger(__name__)


async def log_event(
    db: AsyncSession,
    event_type: str,
    channel: str | None = None,
    user_id: int | None = None,
    details: str | None = None,
    actor: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Enregistre un événement structuré."""
    db.add(
        EventLog(
            event_type=event_type,
            user_id=user_id,
            channel=channel,
            details=details,
            actor=actor,
            ip_address=ip_address,
        )
    )
    logger.info(
        "event=%s channel=%s user_id=%s",
        event_type,
        channel,
        user_id,
    )


async def get_or_create_user(
    db: AsyncSession,
    external_id: str,
    channel: str,
    username: str | None = None,
    first_name: str | None = None,
    language: str | None = None,
) -> User:
    """Récupère ou crée un utilisateur."""
    result = await db.execute(
        select(User).where(User.external_id == external_id)
    )
    user = result.scalar_one_or_none()
    lang = normalize_language(language)
    if user is None:
        user = User(
            external_id=external_id,
            channel=channel,
            username=username,
            first_name=first_name,
            language=lang,
            plan=PlanType.FREE,
        )
        db.add(user)
        await db.flush()
        await log_event(
            db,
            "user_registered",
            channel=channel,
            user_id=user.id,
        )
    else:
        user.username = username or user.username
        user.first_name = first_name or user.first_name
        if language:
            user.language = lang
        user.last_active_at = datetime.now(timezone.utc)
    return user


async def get_history(
    db: AsyncSession,
    user_id: int,
) -> list[dict[str, str]]:
    """Charge l'historique récent depuis PostgreSQL."""
    result = await db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(settings.max_history_messages)
    )
    rows = list(reversed(result.scalars().all()))
    return [
        {
            "role": m.role,
            "content": decrypt_text(m.content, m.is_encrypted),
        }
        for m in rows
    ]


async def save_message(
    db: AsyncSession,
    user_id: int,
    role: str,
    content: str,
    is_crisis: bool = False,
) -> None:
    """Persiste un message (chiffré si configuré)."""
    stored, encrypted = encrypt_text(content)
    db.add(
        Message(
            user_id=user_id,
            role=role,
            content=stored,
            is_crisis=is_crisis,
            is_encrypted=encrypted,
        )
    )


async def clear_history(
    db: AsyncSession,
    external_id: str,
    channel: str,
) -> bool:
    """Efface l'historique d'un utilisateur."""
    result = await db.execute(
        select(User).where(User.external_id == external_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return False
    await db.execute(
        delete(Message).where(Message.user_id == user.id)
    )
    await log_event(
        db,
        "history_cleared",
        channel=channel,
        user_id=user.id,
    )
    return True


async def update_profile(
    db: AsyncSession,
    external_id: str,
    language: str | None = None,
    goals: str | None = None,
    timezone_name: str | None = None,
    notify_enabled: bool | None = None,
) -> User | None:
    """Met à jour le profil utilisateur."""
    result = await db.execute(
        select(User).where(User.external_id == external_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if language is not None:
        user.language = normalize_language(language)
    if goals is not None:
        user.goals = goals
    if timezone_name is not None:
        user.timezone = timezone_name
    if notify_enabled is not None:
        user.notify_enabled = notify_enabled
    return user


async def process_chat(
    db: AsyncSession,
    quota: QuotaService,
    payload: ChatRequest,
) -> ChatResponse:
    """Pipeline central de chat."""
    text = payload.message.strip()
    if len(text) > settings.max_message_length:
        return ChatResponse(
            reply="",
            error_code="message_too_long",
        )

    user = await get_or_create_user(
        db,
        payload.external_id,
        payload.channel,
        payload.username,
        payload.first_name,
        payload.language,
    )

    if not await quota.check_rate_limit(payload.external_id):
        await log_event(
            db,
            "rate_limit_hit",
            channel=payload.channel,
            user_id=user.id,
        )
        return ChatResponse(reply="", error_code="rate_limit")

    allowed, remaining = await quota.check_and_consume_quota(
        payload.external_id,
        user.plan.value,
    )
    if not allowed:
        await log_event(
            db,
            "quota_exceeded",
            channel=payload.channel,
            user_id=user.id,
            details=user.plan.value,
        )
        return ChatResponse(
            reply="",
            error_code="quota_exceeded",
            quota_remaining=0,
        )

    if is_crisis_message(text):
        reply = crisis_text(user.language)
        await save_message(db, user.id, "user", text, is_crisis=True)
        await save_message(
            db, user.id, "assistant", reply, is_crisis=True
        )
        await log_event(
            db,
            "crisis_detected",
            channel=payload.channel,
            user_id=user.id,
        )
        await notify_crisis(
            payload.external_id,
            payload.channel,
            user.id,
        )
        return ChatResponse(
            reply=reply,
            is_crisis=True,
            quota_remaining=remaining,
        )

    history = await get_history(db, user.id)

    try:
        reply = await generate_reply(
            history,
            text,
            language=user.language,
            goals=user.goals,
        )
    except AIServiceError:
        await log_event(
            db,
            "openai_error",
            channel=payload.channel,
            user_id=user.id,
        )
        return ChatResponse(reply="", error_code="openai_error")

    await save_message(db, user.id, "user", text)
    await save_message(db, user.id, "assistant", reply)
    await log_event(
        db,
        "message_sent",
        channel=payload.channel,
        user_id=user.id,
    )

    return ChatResponse(
        reply=reply,
        quota_remaining=remaining,
    )
