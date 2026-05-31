"""Client OpenAI et génération des réponses."""

import logging
from typing import Any

from openai import AsyncOpenAI
from openai import APIConnectionError
from openai import APIStatusError
from openai import APITimeoutError
from openai import RateLimitError

from config import OPENAI_API_KEY
from config import OPENAI_MODEL
from config import OPENAI_TEMPERATURE
from config import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


class AIServiceError(Exception):
    """Erreur lors de l'appel au service IA."""


def _get_client() -> AsyncOpenAI:
    """Retourne le client OpenAI singleton."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    return _client


def _build_messages(
    history: list[dict[str, str]],
    query: str,
) -> list[dict[str, str]]:
    """Construit la liste de messages pour l'API OpenAI."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": query})
    return messages


async def get_answer(
    history: list[dict[str, str]],
    query: str,
) -> str:
    """
    Envoie la requête à OpenAI et retourne la réponse textuelle.

    Lève AIServiceError en cas d'échec API.
    """
    messages = _build_messages(history, query)
    try:
        response = await _get_client().chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=1024,
        )
    except RateLimitError as exc:
        logger.warning("OpenAI rate limit atteint")
        raise AIServiceError("rate_limit") from exc
    except APITimeoutError as exc:
        logger.warning("OpenAI timeout")
        raise AIServiceError("timeout") from exc
    except APIConnectionError as exc:
        logger.warning("OpenAI connexion impossible")
        raise AIServiceError("connection") from exc
    except APIStatusError as exc:
        logger.error(
            "OpenAI API error status=%s",
            exc.status_code,
        )
        raise AIServiceError("api_error") from exc
    except Exception as exc:
        logger.exception("Erreur OpenAI inattendue")
        raise AIServiceError("unknown") from exc

    content = _extract_content(response)
    if not content:
        raise AIServiceError("empty_response")
    return content


def _extract_content(response: Any) -> str | None:
    """Extrait le contenu textuel de la réponse OpenAI."""
    try:
        return response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        return None
