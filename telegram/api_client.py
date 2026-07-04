"""Client HTTP vers le backend."""

import logging

import httpx

from config import BACKEND_API_KEY
from config import BACKEND_URL
from config import CHANNEL

logger = logging.getLogger(__name__)

_HEADERS = {"X-API-Key": BACKEND_API_KEY}
_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class BackendError(Exception):
    """Erreur de communication avec le backend."""

    def __init__(self, error_code: str | None = None) -> None:
        self.error_code = error_code
        super().__init__(error_code or "backend_error")


async def send_chat(
    external_id: str,
    message: str,
    username: str | None = None,
    first_name: str | None = None,
) -> dict:
    """Envoie un message au backend."""
    payload = {
        "external_id": external_id,
        "channel": CHANNEL,
        "message": message,
        "username": username,
        "first_name": first_name,
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(
                f"{BACKEND_URL}/api/v1/chat",
                json=payload,
                headers=_HEADERS,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.error("Backend chat error: %s", exc)
        raise BackendError("connection") from exc


async def clear_history(external_id: str) -> bool:
    """Efface l'historique via le backend."""
    payload = {
        "external_id": external_id,
        "channel": CHANNEL,
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.request(
                "DELETE",
                f"{BACKEND_URL}/api/v1/chat/history",
                json=payload,
                headers=_HEADERS,
            )
            response.raise_for_status()
            data = response.json()
            return bool(data.get("cleared"))
    except httpx.HTTPError as exc:
        logger.error("Backend clear error: %s", exc)
        raise BackendError("connection") from exc
