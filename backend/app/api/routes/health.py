"""Health check enrichi."""

from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.services.quota_service import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Vérifie API, DB et Redis."""
    status = {"status": "ok", "db": "ok", "redis": "ok"}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        status["db"] = "error"
        status["status"] = "degraded"
    try:
        redis_client = await get_redis()
        await redis_client.ping()
    except Exception:
        status["redis"] = "error"
        status["status"] = "degraded"
    return status
