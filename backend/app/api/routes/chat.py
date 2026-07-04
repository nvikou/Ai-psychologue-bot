"""Routes chat."""

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.schemas import ChatRequest
from app.schemas import ChatResponse
from app.schemas import ClearHistoryRequest
from app.services.chat_service import clear_history
from app.services.chat_service import process_chat
from app.services.quota_service import QuotaService
from app.services.quota_service import get_redis

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> ChatResponse:
    """Endpoint central de conversation."""
    redis_client = await get_redis()
    quota = QuotaService(redis_client)
    return await process_chat(db, quota, payload)


@router.delete("/history")
async def delete_history(
    payload: ClearHistoryRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> dict[str, bool]:
    """Efface l'historique d'un utilisateur."""
    cleared = await clear_history(
        db,
        payload.external_id,
        payload.channel,
    )
    return {"cleared": cleared}
