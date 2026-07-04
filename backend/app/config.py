"""Configuration du backend."""

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Variables d'environnement du backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = (
        "postgresql+asyncpg://psychologue:psychologue@postgres:5432"
        "/psychologue"
    )
    redis_url: str = "redis://redis:6379/0"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7

    backend_api_key: str = Field(default="", alias="BACKEND_API_KEY")
    admin_api_key: str = Field(default="", alias="ADMIN_API_KEY")

    max_message_length: int = 2000
    max_history_messages: int = 20
    rate_limit_seconds: float = 2.0

    free_daily_quota: int = 30
    premium_daily_quota: int = 500

    log_level: str = "INFO"

    system_prompt: str = """You are Dr. Émile, a warm and experienced \
clinical psychologist with 20 years of practice. You chat with \
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

With this context, please chat with the user in the \
character of Dr. Émile — a caring psychologist who listens deeply \
and helps them explore their emotions with warmth, clarity, and \
respect."""

    crisis_keywords: tuple[str, ...] = (
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

    crisis_response: str = (
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


settings = Settings()
