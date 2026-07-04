"""Schémas Pydantic API."""

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.models import PlanType


class ChatRequest(BaseModel):
    """Requête de chat multi-canal."""

    external_id: str = Field(..., min_length=1, max_length=128)
    channel: str = Field(..., min_length=1, max_length=32)
    message: str = Field(..., min_length=1)
    username: str | None = None
    first_name: str | None = None


class ChatResponse(BaseModel):
    """Réponse de chat."""

    reply: str
    is_crisis: bool = False
    quota_remaining: int | None = None
    error_code: str | None = None


class ClearHistoryRequest(BaseModel):
    """Effacement d'historique."""

    external_id: str = Field(..., min_length=1, max_length=128)
    channel: str = Field(..., min_length=1, max_length=32)


class UserOut(BaseModel):
    """Utilisateur exposé via API."""

    id: int
    external_id: str
    channel: str
    username: str | None
    first_name: str | None
    plan: PlanType
    message_count: int = 0
    created_at: datetime
    last_active_at: datetime

    model_config = {"from_attributes": True}


class StatsOut(BaseModel):
    """Statistiques globales."""

    total_users: int
    active_today: int
    total_messages: int
    messages_today: int
    crisis_events_today: int
    users_by_plan: dict[str, int]
    users_by_channel: dict[str, int]


class PlanUpdate(BaseModel):
    """Mise à jour du plan utilisateur."""

    plan: PlanType


class EventOut(BaseModel):
    """Événement structuré."""

    id: int
    event_type: str
    channel: str | None
    details: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
