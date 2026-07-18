"""Routes web landing et pages légales."""

from pathlib import Path

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings

router = APIRouter(tags=["web"])

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parents[2] / "templates")
)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Page d'accueil : salutation + lien Telegram."""
    username = settings.telegram_bot_username.lstrip("@")
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "telegram_url": f"https://t.me/{username}",
            "telegram_username": username,
        },
    )


@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request) -> HTMLResponse:
    """Politique de confidentialité."""
    return templates.TemplateResponse(
        request,
        "privacy.html",
        {"retention_days": settings.message_retention_days},
    )


@router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request) -> HTMLResponse:
    """Conditions d'utilisation."""
    return templates.TemplateResponse(request, "terms.html", {})
