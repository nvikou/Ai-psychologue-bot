"""Détection de crise."""

from app.config import settings


def is_crisis_message(text: str) -> bool:
    """Détecte les mots-clés de détresse grave."""
    lowered = text.lower()
    return any(kw in lowered for kw in settings.crisis_keywords)
