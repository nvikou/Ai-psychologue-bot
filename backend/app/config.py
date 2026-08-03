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
    admin_jwt_secret: str = Field(
        default="change-me-admin-jwt-secret",
        alias="ADMIN_JWT_SECRET",
    )
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")

    max_message_length: int = 2000
    max_history_messages: int = 20
    rate_limit_seconds: float = 2.0
    ip_rate_limit_per_minute: int = 60

    free_daily_quota: int = 30
    premium_daily_quota: int = 500

    message_retention_days: int = 90
    default_language: str = "en"
    cors_origins: str = "*"

    sentry_dsn: str = ""
    crisis_webhook_url: str = ""
    public_base_url: str = "http://localhost:8000"
    telegram_bot_username: str = Field(
        default="ai_psychologueBot",
        alias="TELEGRAM_BOT_USERNAME",
    )

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
- Listen first. Help the user express what they feel.
- Reflect and check understanding before giving advice.
- Ask open, gentle questions when exploring.
- When advising, give practical coping ideas and small next steps.
- Keep replies natural and warm: 2–4 short paragraphs, clear prose, \
no jargon unless you explain it simply.
- Always reply in the user's preferred language when specified.

IMPORTANT SESSION RULE:
- Follow the CURRENT STAGE instructions strictly when provided.
- Do not jump to advice before the advise stage.

SAFETY & LIMITS (always follow):
- You are an AI playing the role of a supportive psychologist — \
not a licensed professional. Never claim real credentials.
- Never diagnose mental health conditions or prescribe medication.
- Encourage seeing a real therapist when problems are serious or \
long-lasting."""

    prompt_closing: str = (
        "With this context, please chat with the user in the "
        "character of Dr. Émile — a caring psychologist who listens "
        "deeply and helps them explore their emotions with warmth, "
        "clarity, and respect."
    )

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
        "me suicider",
        "envie de mourir",
        "me tuer",
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
        "• *112* — European emergency number\n"
        "• *3114* — Suicide prevention (France, 24/7)\n\n"
        "You are not alone. Trained professionals are available now."
    )


settings = Settings()
