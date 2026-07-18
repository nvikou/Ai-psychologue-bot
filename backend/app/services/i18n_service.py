"""Chaînes i18n et réponses localisées."""

from app.config import settings

SUPPORTED_LANGUAGES = ("en", "fr", "es")

CRISIS_RESPONSES = {
    "en": settings.crisis_response,
    "fr": (
        "Je suis profondément concerné(e) par ce que vous partagez. "
        "Votre sécurité est la priorité absolue.\n\n"
        "Je ne suis pas un professionnel de santé et je ne peux pas "
        "vous accompagner dans une situation aussi grave.\n\n"
        "Contactez immédiatement une aide d'urgence :\n"
        "• *3114* — Prévention du suicide (France, 24h/24)\n"
        "• *15* — SAMU\n"
        "• *112* — Urgences européennes\n"
        "• *988* — Suicide & Crisis Lifeline (US)\n\n"
        "Vous n'êtes pas seul(e). Des professionnels sont disponibles."
    ),
    "es": (
        "Me preocupa profundamente lo que estás compartiendo. "
        "Tu seguridad es la prioridad absoluta.\n\n"
        "No soy un profesional de la salud y no puedo acompañarte "
        "en una situación tan grave.\n\n"
        "Contacta ayuda de emergencia de inmediato:\n"
        "• *112* — Emergencias europeas\n"
        "• *911* — Emergencias (US)\n"
        "• *988* — Línea de crisis (US)\n\n"
        "No estás solo/a. Hay profesionales disponibles ahora."
    ),
}


def normalize_language(lang: str | None) -> str:
    """Normalise une langue vers une valeur supportée."""
    if not lang:
        return settings.default_language
    code = lang.strip().lower()[:2]
    if code in SUPPORTED_LANGUAGES:
        return code
    return settings.default_language


def crisis_text(lang: str | None) -> str:
    """Réponse de crise localisée."""
    return CRISIS_RESPONSES[normalize_language(lang)]


def language_instruction(lang: str | None) -> str:
    """Instruction de langue pour le prompt système."""
    code = normalize_language(lang)
    names = {"en": "English", "fr": "French", "es": "Spanish"}
    return f"Always reply in {names[code]}."
