"""Point d'entrée du bot Telegram (polling ou webhook)."""

import asyncio
import logging
import os
import sys

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web

import handlers
from config import LOG_LEVEL
from config import TELEGRAM_TOKEN
from config import validate_config

WEBHOOK_MODE = os.getenv("TELEGRAM_WEBHOOK_MODE", "false").lower() in (
    "1",
    "true",
    "yes",
)
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/telegram/webhook")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()


def _setup_logging() -> None:
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    handlers_list: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
    ]
    log_file = os.getenv("LOG_FILE", "")
    if log_file:
        try:
            handlers_list.append(
                logging.FileHandler(log_file, encoding="utf-8")
            )
        except (OSError, PermissionError):
            pass

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers_list,
        force=True,
    )


async def run_polling() -> None:
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    logger = logging.getLogger(__name__)
    try:
        logger.info("Telegram bot starting (polling)...")
        await dp.start_polling(bot)
    finally:
        logger.info("Telegram bot stopped")
        await bot.session.close()


async def on_startup(bot: Bot) -> None:
    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL is required in webhook mode")
    await bot.set_webhook(f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}")
    logging.getLogger(__name__).info("Webhook set to %s%s", WEBHOOK_URL, WEBHOOK_PATH)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=False)


def run_webhook() -> None:
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(
        app,
        path=WEBHOOK_PATH,
    )
    setup_application(app, dp, bot=bot)
    logging.getLogger(__name__).info(
        "Telegram bot starting (webhook) on %s:%s%s",
        WEBHOOK_HOST,
        WEBHOOK_PORT,
        WEBHOOK_PATH,
    )
    web.run_app(app, host=WEBHOOK_HOST, port=WEBHOOK_PORT)


async def main() -> None:
    validate_config()
    _setup_logging()
    if WEBHOOK_MODE:
        # aiohttp run_app is sync; call from __main__
        raise RuntimeError("Use sync webhook entry")
    await run_polling()


if __name__ == "__main__":
    validate_config()
    _setup_logging()
    if WEBHOOK_MODE:
        run_webhook()
    else:
        asyncio.run(run_polling())
