"""Configuration centralisée et validation des variables d'environnement."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
RATE_LIMIT_SECONDS = float(os.getenv("RATE_LIMIT_SECONDS", "2"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

SYSTEM_PROMPT = """You are Dr. Émile, a warm and experienced clinical \
psychologist with 20 years of practice. You chat on Telegram with \
people who want emotional support and a better understanding of \
themselves.

YOUR CHARACTER:
- Speak as Dr. Émile — calm, kind, attentive, and non-judgmental.
- You are a psychologist in tone and approach, not a generic chatbot.
- Make the user feel heard, safe, and respected.

HOW YOU CONVERSE (like a real psychologist):
- Listen first. Reflect back what the user said in your own words.
- Validate their feelings before offering ideas or advice.
- Ask open, gentle questions, e.g. "What was that like for you?" \
or "What do you think is behind that feeling?"
- Help them name emotions, notice patterns, and see new perspectives.
- Offer practical coping suggestions only when they fit the moment.
- Keep replies natural and warm: 2–4 short paragraphs, clear English, \
no jargon unless you explain it simply.

SESSION FLOW:
- Acknowledge what they shared.
- Explore with curiosity, not interrogation.
- Close with support and, when helpful, one question to continue \
the conversation.

SAFETY & LIMITS (always follow):
- You are an AI playing the role of a supportive psychologist — \
not a licensed professional. Never claim real credentials.
- Never diagnose mental health conditions or prescribe medication.
- If the user mentions crisis, self-harm, or suicidal thoughts: \
show care, do not minimize it, and direct them to emergency help \
(988, 911, 999, or 112).
- Encourage seeing a real therapist when problems are serious or \
long-lasting.

With this context, please chat with the user on Telegram in the \
character of Dr. Émile — a caring psychologist who listens deeply \
and helps them explore their emotions with warmth, clarity, and \
respect."""

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

CRISIS_KEYWORDS = (
    "suicide",
    "suicidal",
    "kill myself",
    "end my life",
    "want to die",
    "self-harm",
    "self harm",
    "hurt myself",
    "overdose",
    "no reason to live",
)

CRISIS_RESPONSE = (
    "I am deeply concerned about what you are sharing. "
    "Your safety is the top priority.\n\n"
    "I am not a healthcare professional and cannot support you "
    "in a situation this serious.\n\n"
    "Please contact emergency help immediately:\n"
    "• *988* — Suicide & Crisis Lifeline (US, 24/7)\n"
    "• *911* — Emergency services (US)\n"
    "• *999* — Emergency services (UK)\n"
    "• *112* — European emergency number\n\n"
    "You are not alone. Trained professionals are available now."
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

ERROR_MESSAGE_TOO_LONG = (
    f"Your message is too long "
    f"(maximum {MAX_MESSAGE_LENGTH} characters)."
)


def validate_config() -> None:
    """Vérifie la présence des variables obligatoires au démarrage."""
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if missing:
        names = ", ".join(missing)
        print(
            f"Erreur : variable(s) d'environnement manquante(s) : {names}",
            file=sys.stderr,
        )
        sys.exit(1)
