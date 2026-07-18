"""Routes admin, dashboard et audit."""

from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import create_admin_token
from app.dependencies import verify_admin_key
from app.models import AdminAuditLog
from app.models import Message
from app.schemas import AdminTokenOut
from app.schemas import EventOut
from app.schemas import PlanUpdate
from app.schemas import StatsOut
from app.schemas import UserOut
from app.services.gdpr_service import purge_expired_messages
from app.services.stats_service import get_stats
from app.services.stats_service import list_recent_events
from app.services.stats_service import list_users
from app.services.stats_service import update_user_plan

router = APIRouter(prefix="/admin", tags=["admin"])

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parents[2] / "templates")
)


async def _audit(
    db: AsyncSession,
    action: str,
    actor: str,
    request: Request,
    target: str | None = None,
    details: str | None = None,
) -> None:
    ip = request.client.host if request.client else None
    db.add(
        AdminAuditLog(
            action=action,
            actor=actor,
            target=target,
            details=details,
            ip_address=ip,
        )
    )


@router.post("/token", response_model=AdminTokenOut)
async def admin_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(verify_admin_key),
) -> AdminTokenOut:
    """Échange une clé admin contre un JWT (8h)."""
    await _audit(db, "admin_token_issued", actor, request)
    return AdminTokenOut(access_token=create_admin_token())


@router.get("/stats", response_model=StatsOut)
async def admin_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(verify_admin_key),
) -> StatsOut:
    """Statistiques JSON pour clients admin."""
    await _audit(db, "view_stats", actor, request)
    return await get_stats(db)


@router.get("/users", response_model=list[UserOut])
async def admin_users(
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(verify_admin_key),
) -> list[UserOut]:
    """Liste des utilisateurs."""
    await _audit(db, "list_users", actor, request)
    return await list_users(db)


@router.get("/events", response_model=list[EventOut])
async def admin_events(
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(verify_admin_key),
) -> list[EventOut]:
    """Événements récents."""
    await _audit(db, "list_events", actor, request)
    return await list_recent_events(db)


@router.patch("/users/{user_id}/plan", response_model=UserOut)
async def set_user_plan(
    user_id: int,
    payload: PlanUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(verify_admin_key),
) -> UserOut:
    """Change le plan d'un utilisateur (free/premium)."""
    user = await update_user_plan(db, user_id, payload.plan)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await _audit(
        db,
        "update_plan",
        actor,
        request,
        target=str(user_id),
        details=payload.plan.value,
    )
    count = await db.scalar(
        select(func.count(Message.id)).where(
            Message.user_id == user.id
        )
    ) or 0
    return UserOut(
        id=user.id,
        external_id=user.external_id,
        channel=user.channel,
        username=user.username,
        first_name=user.first_name,
        language=user.language,
        plan=user.plan,
        message_count=count,
        created_at=user.created_at,
        last_active_at=user.last_active_at,
    )


@router.post("/retention/purge")
async def retention_purge(
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(verify_admin_key),
) -> dict[str, int]:
    """Purge manuelle des messages expirés (RGPD rétention)."""
    deleted = await purge_expired_messages(db)
    await _audit(
        db,
        "retention_purge",
        actor,
        request,
        details=f"deleted={deleted}",
    )
    return {"deleted": deleted}


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: str = Depends(verify_admin_key),
) -> HTMLResponse:
    """Dashboard HTML."""
    await _audit(db, "view_dashboard", actor, request)
    stats = await get_stats(db)
    users = await list_users(db, limit=20)
    events = await list_recent_events(db, limit=20)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "stats": stats,
            "users": users,
            "events": events,
        },
    )
