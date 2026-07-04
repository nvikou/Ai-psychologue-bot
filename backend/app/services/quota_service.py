"""Client Redis pour rate limiting et quotas."""

import logging
from datetime import date

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)

_redis: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Retourne le client Redis singleton."""
    global _redis
    if _redis is None:
        _redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def close_redis() -> None:
    """Ferme la connexion Redis."""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


class QuotaService:
    """Rate limit et quotas journaliers par plan."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    async def check_rate_limit(self, external_id: str) -> bool:
        """True si la requête est autorisée (pas trop rapide)."""
        key = f"rate:{external_id}"
        exists = await self._redis.exists(key)
        if exists:
            return False
        await self._redis.setex(
            key,
            int(settings.rate_limit_seconds),
            "1",
        )
        return True

    def _daily_limit(self, plan: str) -> int:
        if plan == "premium":
            return settings.premium_daily_quota
        return settings.free_daily_quota

    async def check_and_consume_quota(
        self,
        external_id: str,
        plan: str,
    ) -> tuple[bool, int]:
        """
        Consomme un crédit quota journalier.

        Retourne (autorisé, restant).
        """
        today = date.today().isoformat()
        key = f"quota:{external_id}:{today}"
        limit = self._daily_limit(plan)
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, 86400)
        remaining = max(limit - count, 0)
        if count > limit:
            await self._redis.decr(key)
            return False, 0
        return True, remaining

    async def get_remaining_quota(
        self,
        external_id: str,
        plan: str,
    ) -> int:
        """Quota restant sans consommation."""
        today = date.today().isoformat()
        key = f"quota:{external_id}:{today}"
        raw = await self._redis.get(key)
        used = int(raw) if raw else 0
        return max(self._daily_limit(plan) - used, 0)
