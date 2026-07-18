"""Notifications de crise vers un webhook admin (escalade humaine)."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def notify_crisis(
    external_id: str,
    channel: str,
    user_id: int | None = None,
) -> None:
    """Envoie une alerte anonyme vers CRISIS_WEBHOOK_URL si défini."""
    if not settings.crisis_webhook_url:
        return
    payload = {
        "event": "crisis_detected",
        "external_id": external_id,
        "channel": channel,
        "user_id": user_id,
        "message": (
            "A crisis keyword was detected. "
            "Review urgently. Message content is not included."
        ),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(settings.crisis_webhook_url, json=payload)
        logger.info("Crisis webhook notified for user_id=%s", user_id)
    except Exception:
        logger.exception("Crisis webhook failed")
