"""Configuration du bot Telegram (UI uniquement)."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
BACKEND_URL = os.getenv("BACKEND_URL", "http://api:8000").strip()
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "").strip()
CHANNEL = "telegram"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en").strip() or "en"

MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

DISCLAIMER = {
    "en": (
        "⚠️ *Important notice*\n\n"
        "I am an AI assistant, not a mental health professional.\n"
        "My replies do not replace medical or psychological advice.\n\n"
        "If you are in crisis or need urgent help:\n"
        "• *911* — Emergency services (US)\n"
        "• *999* — Emergency services (UK)\n"
        "• *112* — European emergency number\n"
        "• *988* — Suicide & Crisis Lifeline (US, 24/7)\n"
        "• *3114* — Suicide prevention (France)\n\n"
        "How can I listen to you today? 🧠"
    ),
    "fr": (
        "⚠️ *Avertissement important*\n\n"
        "Je suis un assistant IA, pas un professionnel de santé mentale.\n"
        "Mes réponses ne remplacent pas un avis médical.\n\n"
        "En cas d'urgence :\n"
        "• *3114* — Prévention du suicide (France)\n"
        "• *15* — SAMU\n"
        "• *112* — Urgences européennes\n\n"
        "Comment puis-je vous écouter aujourd'hui ? 🧠"
    ),
    "es": (
        "⚠️ *Aviso importante*\n\n"
        "Soy un asistente de IA, no un profesional de salud mental.\n"
        "Mis respuestas no sustituyen consejo médico.\n\n"
        "En una emergencia:\n"
        "• *112* — Emergencias europeas\n"
        "• *911* / *988* — EE.UU.\n\n"
        "¿Cómo puedo escucharte hoy? 🧠"
    ),
}

ERROR_OPENAI = (
    "Sorry, I am experiencing a temporary technical issue. "
    "Please try again in a few moments."
)

ERROR_GENERIC = (
    "An unexpected error occurred. "
    "Please try again later."
)

ERROR_RATE_LIMIT = (
    "Please wait a few seconds before sending another message."
)

ERROR_QUOTA = (
    "You have reached your daily message limit. "
    "Try again tomorrow or upgrade to premium."
)

ERROR_MESSAGE_TOO_LONG = (
    f"Your message is too long "
    f"(maximum {MAX_MESSAGE_LENGTH} characters)."
)

ERROR_BACKEND = (
    "Unable to reach the server. Please try again later."
)


def validate_config() -> None:
    """Vérifie les variables obligatoires du bot."""
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not BACKEND_API_KEY:
        missing.append("BACKEND_API_KEY")
    if missing:
        names = ", ".join(missing)
        print(f"Missing env vars: {names}", file=sys.stderr)
        sys.exit(1)


def external_id(telegram_user_id: int) -> str:
    """Identifiant unique multi-canal."""
    return f"telegram:{telegram_user_id}"


def disclaimer_for(lang_code: str | None) -> str:
    code = (lang_code or DEFAULT_LANGUAGE).lower()[:2]
    return DISCLAIMER.get(code, DISCLAIMER["en"])
