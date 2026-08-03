"""Client OpenAI."""

import logging
from typing import Any

from openai import AsyncOpenAI
from openai import APIConnectionError
from openai import APIStatusError
from openai import APITimeoutError
from openai import RateLimitError

from app.config import settings
from app.services.i18n_service import language_instruction

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


class AIServiceError(Exception):
    """Erreur lors de l'appel au service IA."""


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def generate_reply_with_system(
    history: list[dict[str, str]],
    query: str,
    system_extra: str = "",
) -> str:
    """Génère une réponse avec le prompt système + instructions."""
    system = settings.system_prompt
    if system_extra:
        system = f"{system}\n\n{system_extra}"
    system = f"{system}\n\n{settings.prompt_closing}"

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
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


async def classify_text(
    system: str,
    user: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 32,
) -> str:
    """Appel LLM court pour classification / routage."""
    try:
        response = await _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
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
        logger.exception("OpenAI classify unexpected error")
        raise AIServiceError("unknown") from exc

    content = _extract_content(response)
    if not content:
        raise AIServiceError("empty_response")
    return content.strip()


async def generate_reply(
    history: list[dict[str, str]],
    query: str,
    language: str | None = None,
    goals: str | None = None,
) -> str:
    """Génère une réponse via OpenAI (compatibilité)."""
    extra = language_instruction(language)
    if goals:
        extra += f"\nUser goals/context: {goals}"
    return await generate_reply_with_system(history, query, extra)


def _extract_content(response: Any) -> str | None:
    try:
        return response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        return None
