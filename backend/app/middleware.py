"""Middleware rate limit par IP."""

import logging

from fastapi import Request
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.services.quota_service import get_redis

logger = logging.getLogger(__name__)


class IPRateLimitMiddleware(BaseHTTPMiddleware):
    """Limite le nombre de requêtes par IP et par minute."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in ("/health", "/"):
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        try:
            redis_client = await get_redis()
            key = f"iprate:{client_ip}"
            count = await redis_client.incr(key)
            if count == 1:
                await redis_client.expire(key, 60)
            if count > settings.ip_rate_limit_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"},
                )
        except Exception:
            logger.warning("IP rate limit check failed", exc_info=True)
        return await call_next(request)
