"""Dépendances FastAPI (auth, DB)."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from jose import JWTError
from jose import jwt

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


def create_admin_token() -> str:
    """Crée un JWT admin de courte durée."""
    payload = {
        "sub": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    return jwt.encode(
        payload,
        settings.admin_jwt_secret,
        algorithm="HS256",
    )


def _valid_admin_jwt(token: str) -> bool:
    try:
        data = jwt.decode(
            token,
            settings.admin_jwt_secret,
            algorithms=["HS256"],
        )
        return data.get("sub") == "admin"
    except JWTError:
        return False


async def verify_admin_key(
    x_admin_key: str | None = Header(None, alias="X-Admin-Key"),
    authorization: str | None = Header(None),
    key: str | None = Query(None, description="Admin key for browser"),
) -> str:
    """
    Vérifie l'accès admin.

    Accepte: X-Admin-Key, ?key=, ou Bearer JWT.
    Retourne l'identité acteur pour l'audit.
    """
    if (
        settings.admin_api_key
        and (x_admin_key == settings.admin_api_key or key == settings.admin_api_key)
    ):
        return "admin-key"

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if _valid_admin_jwt(token):
            return "admin-jwt"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin credentials",
    )
