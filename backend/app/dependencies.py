"""Dépendances FastAPI (auth, DB)."""

from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from app.config import settings


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> None:
    """Vérifie la clé API client (bot, web, mobile)."""
    if (
        not settings.backend_api_key
        or x_api_key != settings.backend_api_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


async def verify_admin_key(
    x_admin_key: str | None = Header(None, alias="X-Admin-Key"),
    key: str | None = Query(None, description="Admin key for browser"),
) -> None:
    """Vérifie la clé admin (header ou query pour dashboard)."""
    provided = x_admin_key or key
    if (
        not settings.admin_api_key
        or provided != settings.admin_api_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key",
        )
