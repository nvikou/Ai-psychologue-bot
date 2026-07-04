"""Client OpenAI."""

import logging
from typing import Any

from openai import AsyncOpenAI
from openai import APIConnectionError
from openai import APIStatusError
from openai import APITimeoutError
from openai import RateLimitError

from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


class AIServiceError(Exception):
    """Erreur lors de l'appel au service IA."""


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def generate_reply(
    history: list[dict[str, str]],
    query: str,
) -> str:
    """Génère une réponse via OpenAI."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": settings.system_prompt},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": query})

    try:
        response = await _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=settings.openai_temperature,
            max_tokens=1024,
        )
    except RateLimitError as exc:
        raise AIServiceError("rate_limit") from exc
    except APITimeoutError as exc:
        raise AIServiceError("timeout") from exc
    except APIConnectionError as exc:
        raise AIServiceError("connection") from exc
    except APIStatusError as exc:
        logger.error("OpenAI status=%s", exc.status_code)
        raise AIServiceError("api_error") from exc
    except Exception as exc:
        logger.exception("OpenAI unexpected error")
        raise AIServiceError("unknown") from exc

    content = _extract_content(response)
    if not content:
        raise AIServiceError("empty_response")
    return content


def _extract_content(response: Any) -> str | None:
    try:
        return response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        return None
