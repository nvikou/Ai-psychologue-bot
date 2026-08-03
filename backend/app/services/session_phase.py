"""Gestion de la phase de séance (Redis)."""

import logging

from app.services.quota_service import get_redis

logger = logging.getLogger(__name__)

VALID_PHASES = ("listen", "explore", "reflect", "advise")


async def get_session_phase(external_id: str) -> tuple[str, int]:
    """Retourne (phase, turn_count) pour un utilisateur."""
    redis_client = await get_redis()
    phase = await redis_client.get(f"phase:{external_id}")
    turns = await redis_client.get(f"turns:{external_id}")
    if phase not in VALID_PHASES:
        phase = "listen"
    turn_count = int(turns) if turns else 0
    return phase, turn_count


async def set_session_phase(
    external_id: str,
    phase: str,
    turn_count: int,
) -> None:
    """Persiste la phase de séance (7 jours)."""
    if phase not in VALID_PHASES:
        phase = "listen"
    redis_client = await get_redis()
    await redis_client.setex(f"phase:{external_id}", 7 * 86400, phase)
    await redis_client.setex(
        f"turns:{external_id}",
        7 * 86400,
        str(turn_count),
    )
    logger.info(
        "session phase=%s turns=%s external_id=%s",
        phase,
        turn_count,
        external_id,
    )


async def reset_session_phase(external_id: str) -> None:
    """Réinitialise la phase (ex: clear history)."""
    redis_client = await get_redis()
    await redis_client.delete(f"phase:{external_id}")
    await redis_client.delete(f"turns:{external_id}")
