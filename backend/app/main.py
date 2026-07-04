"""Application FastAPI principale."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import admin
from app.api.routes import chat
from app.api.routes import health
from app.config import settings
from app.database import Base
from app.database import engine
from app.services.quota_service import close_redis


def _setup_logging() -> None:
    level = getattr(logging, settings.log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format=(
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        ),
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def _validate_settings() -> None:
    missing = []
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not settings.backend_api_key:
        missing.append("BACKEND_API_KEY")
    if not settings.admin_api_key:
        missing.append("ADMIN_API_KEY")
    if missing:
        names = ", ".join(missing)
        print(f"Missing env vars: {names}", file=sys.stderr)
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisation et fermeture."""
    _validate_settings()
    _setup_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.getLogger(__name__).info("Backend started")
    yield
    await close_redis()
    await engine.dispose()
    logging.getLogger(__name__).info("Backend stopped")


app = FastAPI(
    title="Dr. Émile Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
