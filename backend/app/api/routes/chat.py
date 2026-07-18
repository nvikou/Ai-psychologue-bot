"""Routes chat, profil et RGPD."""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.schemas import ChatRequest
from app.schemas import ChatResponse
from app.schemas import ClearHistoryRequest
from app.schemas import GdprRequest
from app.schemas import ProfileOut
from app.schemas import ProfileUpdate
from app.services.chat_service import clear_history
from app.services.chat_service import get_or_create_user
from app.services.chat_service import process_chat
from app.services.chat_service import update_profile
from app.services.gdpr_service import delete_user_data
from app.services.gdpr_service import export_user_data
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


@router.put("/profile", response_model=ProfileOut)
async def put_profile(
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> ProfileOut:
    """Crée/met à jour le profil utilisateur."""
    user = await get_or_create_user(
        db,
        payload.external_id,
        payload.channel,
        payload.username,
        payload.first_name,
        payload.language,
    )
    user = await update_profile(
        db,
        payload.external_id,
        language=payload.language,
        goals=payload.goals,
        timezone_name=payload.timezone,
        notify_enabled=payload.notify_enabled,
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileOut.model_validate(user)


@router.post("/gdpr/export")
async def gdpr_export(
    payload: GdprRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> dict:
    """Export des données personnelles (portabilité)."""
    data = await export_user_data(db, payload.external_id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return data


@router.post("/gdpr/delete")
async def gdpr_delete(
    payload: GdprRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> dict[str, bool]:
    """Droit à l'oubli : suppression complète du compte."""
    deleted = await delete_user_data(db, payload.external_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}
