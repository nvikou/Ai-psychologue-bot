"""Point d'entrée du bot Telegram."""

import asyncio
import logging
import os
import sys

from aiogram import Bot
from aiogram import Dispatcher

import handlers
from config import LOG_LEVEL
from config import TELEGRAM_TOKEN
from config import validate_config


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


async def main() -> None:
    validate_config()
    _setup_logging()
    logger = logging.getLogger(__name__)

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(handlers.router)

    try:
        logger.info("Telegram bot starting...")
        await dp.start_polling(bot)
    finally:
        logger.info("Telegram bot stopped")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
