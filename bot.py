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
    """Configure le logging applicatif."""
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    handlers_list: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
    ]
    log_file = os.getenv("LOG_FILE", "bot.log")
    if log_file:
        try:
            handlers_list.append(
                logging.FileHandler(log_file, encoding="utf-8")
            )
        except (OSError, PermissionError):
            logging.basicConfig(level=level, force=True)
            logging.warning(
                "Impossible d'écrire dans %s, logs stdout uniquement",
                log_file,
            )
            logging.getLogger("httpx").setLevel(logging.WARNING)
            logging.getLogger("openai").setLevel(logging.WARNING)
            return

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers_list,
        force=True,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


async def main() -> None:
    """Démarre le polling Telegram."""
    validate_config()
    _setup_logging()
    logger = logging.getLogger(__name__)

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(handlers.router)

    try:
        logger.info("Démarrage du bot...")
        await dp.start_polling(bot)
    finally:
        logger.info("Arrêt du bot...")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
