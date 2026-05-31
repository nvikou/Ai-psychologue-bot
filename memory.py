"""Gestion thread-safe de la mémoire conversationnelle."""

import asyncio
import logging
import time
from collections import defaultdict

from config import MAX_HISTORY_MESSAGES, RATE_LIMIT_SECONDS

logger = logging.getLogger(__name__)


class ConversationStore:
    """Stockage en mémoire des conversations et du rate limiting."""

    def __init__(
        self,
        max_messages: int = MAX_HISTORY_MESSAGES,
        rate_limit_seconds: float = RATE_LIMIT_SECONDS,
    ) -> None:
        self._max_messages = max_messages
        self._rate_limit_seconds = rate_limit_seconds
        self._history: dict[int, list[dict[str, str]]] = defaultdict(list)
        self._last_request: dict[int, float] = {}
        self._lock = asyncio.Lock()

    async def get_history(self, user_id: int) -> list[dict[str, str]]:
        """Retourne une copie de l'historique d'un utilisateur."""
        async with self._lock:
            return list(self._history[user_id])

    async def append_exchange(
        self,
        user_id: int,
        user_text: str,
        assistant_text: str,
    ) -> None:
        """Ajoute un échange user/assistant et limite la taille."""
        async with self._lock:
            history = self._history[user_id]
            history.append({"role": "user", "content": user_text})
            history.append(
                {"role": "assistant", "content": assistant_text}
            )
            if len(history) > self._max_messages:
                self._history[user_id] = history[-self._max_messages :]
            logger.info(
                "Historique mis à jour pour user_id=%s (%s messages)",
                user_id,
                len(self._history[user_id]),
            )

    async def clear(self, user_id: int) -> None:
        """Efface l'historique d'un utilisateur."""
        async with self._lock:
            self._history[user_id] = []
            self._last_request.pop(user_id, None)
            logger.info("Historique effacé pour user_id=%s", user_id)

    async def check_rate_limit(self, user_id: int) -> bool:
        """
        Vérifie le rate limit.

        Retourne True si la requête est autorisée.
        """
        async with self._lock:
            now = time.monotonic()
            last = self._last_request.get(user_id, 0.0)
            if now - last < self._rate_limit_seconds:
                return False
            self._last_request[user_id] = now
            return True
