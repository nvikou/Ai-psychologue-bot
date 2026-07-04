"""Configuration du bot Telegram (UI uniquement)."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
BACKEND_URL = os.getenv("BACKEND_URL", "http://api:8000").strip()
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "").strip()
CHANNEL = "telegram"

MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

DISCLAIMER = (
    "⚠️ *Important notice*\n\n"
    "I am an AI assistant, not a mental health professional.\n"
    "My replies do not replace medical or psychological advice.\n\n"
    "If you are in crisis or need urgent help:\n"
    "• *911* — Emergency services (US)\n"
    "• *999* — Emergency services (UK)\n"
    "• *112* — European emergency number\n"
    "• *988* — Suicide & Crisis Lifeline (US, 24/7)\n\n"
    "How can I listen to you today? 🧠"
)

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
