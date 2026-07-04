"""Handlers Telegram — client fin du backend."""

import asyncio
import logging

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message

from api_client import BackendError
from api_client import clear_history
from api_client import send_chat
from config import DISCLAIMER
from config import ERROR_BACKEND
from config import ERROR_GENERIC
from config import ERROR_MESSAGE_TOO_LONG
from config import ERROR_OPENAI
from config import ERROR_QUOTA
from config import ERROR_RATE_LIMIT
from config import MAX_MESSAGE_LENGTH
from config import external_id

logger = logging.getLogger(__name__)

router = Router()


def _kb_clear_memory() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑️ Clear history",
                    callback_data="clear_memory",
                )
            ]
        ]
    )


@router.startup()
async def set_menu_button(bot: Bot) -> None:
    """Configure le menu ; n'interrompt jamais le démarrage."""
    commands = [
        BotCommand(command="start", description="Start"),
        BotCommand(command="help", description="Help and disclaimer"),
    ]
    for attempt in range(1, 4):
        try:
            await bot.set_my_commands(commands)
            logger.info("Bot menu commands set")
            return
        except Exception:
            logger.warning(
                "set_my_commands failed (attempt %s/3)",
                attempt,
                exc_info=True,
            )
            if attempt < 3:
                await asyncio.sleep(2 * attempt)
    logger.warning(
        "Menu not configured — polling will continue anyway"
    )


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    uid = external_id(message.from_user.id)
    try:
        await clear_history(uid)
    except BackendError:
        pass
    await message.answer(DISCLAIMER, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(DISCLAIMER, parse_mode="Markdown")


@router.callback_query(F.data == "clear_memory")
async def handle_clear_callback(callback: CallbackQuery) -> None:
    uid = external_id(callback.from_user.id)
    try:
        await clear_history(uid)
        await callback.answer("History cleared.")
    except BackendError:
        await callback.answer("Could not clear history.")
    if callback.message:
        await callback.message.delete()


@router.message(F.text)
async def handle_dialog(message: Message, bot: Bot) -> None:
    user = message.from_user
    uid = external_id(user.id)
    text = message.text.strip() if message.text else ""

    logger.info("Telegram message user_id=%s len=%s", user.id, len(text))

    if not text:
        return

    if len(text) > MAX_MESSAGE_LENGTH:
        await message.answer(ERROR_MESSAGE_TOO_LONG)
        return

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        data = await send_chat(
            uid,
            text,
            username=user.username,
            first_name=user.first_name,
        )
    except BackendError:
        await message.answer(ERROR_BACKEND)
        return
    except Exception:
        logger.exception("Unexpected error user_id=%s", user.id)
        await message.answer(ERROR_GENERIC)
        return

    error_code = data.get("error_code")
    if error_code == "rate_limit":
        await message.answer(ERROR_RATE_LIMIT)
        return
    if error_code == "quota_exceeded":
        await message.answer(ERROR_QUOTA)
        return
    if error_code == "message_too_long":
        await message.answer(ERROR_MESSAGE_TOO_LONG)
        return
    if error_code == "openai_error":
        await message.answer(ERROR_OPENAI)
        return
    if error_code:
        await message.answer(ERROR_GENERIC)
        return

    reply = data.get("reply", "")
    if not reply:
        await message.answer(ERROR_GENERIC)
        return

    parse_mode = "Markdown" if data.get("is_crisis") else None
    await message.answer(reply, parse_mode=parse_mode)

    if not data.get("is_crisis"):
        quota = data.get("quota_remaining")
        footer = "Ask your next question or clear the memory:"
        if quota is not None:
            footer += f"\n\n_Messages left today: {quota}_"
        await message.answer(
            footer,
            parse_mode="Markdown",
            reply_markup=_kb_clear_memory(),
        )

    logger.info("Reply sent to user_id=%s", user.id)
