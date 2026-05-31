"""Handlers Telegram du bot psychologue."""

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

from config import CRISIS_KEYWORDS
from config import CRISIS_RESPONSE
from config import DISCLAIMER
from config import ERROR_GENERIC
from config import ERROR_MESSAGE_TOO_LONG
from config import ERROR_OPENAI
from config import ERROR_RATE_LIMIT
from config import MAX_MESSAGE_LENGTH
from libs import AIServiceError
from libs import get_answer
from memory import ConversationStore

logger = logging.getLogger(__name__)

router = Router()
store = ConversationStore()


def _kb_clear_memory() -> InlineKeyboardMarkup:
    """Clavier inline pour effacer l'historique."""
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


def _is_crisis_message(text: str) -> bool:
    """Détecte les mots-clés de détresse grave."""
    lowered = text.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)


@router.startup()
async def set_menu_button(bot: Bot) -> None:
    """Configure le menu des commandes du bot."""
    commands = [
        BotCommand(command="start", description="Start"),
        BotCommand(command="help", description="Help and disclaimer"),
    ]
    await bot.set_my_commands(commands)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Commande /start : reset mémoire et disclaimer."""
    user_id = message.from_user.id
    await store.clear(user_id)
    await message.answer(DISCLAIMER, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Commande /help : rappel des limites du bot."""
    await message.answer(DISCLAIMER, parse_mode="Markdown")


@router.callback_query(F.data == "clear_memory")
async def handle_clear_callback(callback: CallbackQuery) -> None:
    """Efface l'historique via le bouton inline."""
    user_id = callback.from_user.id
    await store.clear(user_id)
    await callback.answer("History cleared.")
    if callback.message:
        await callback.message.delete()


@router.message(F.text)
async def handle_dialog(message: Message, bot: Bot) -> None:
    """Traite un message texte de l'utilisateur."""
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    logger.info("Message reçu de user_id=%s (len=%s)", user_id, len(text))

    if not text:
        return

    if len(text) > MAX_MESSAGE_LENGTH:
        await message.answer(ERROR_MESSAGE_TOO_LONG)
        return

    if not await store.check_rate_limit(user_id):
        await message.answer(ERROR_RATE_LIMIT)
        return

    if _is_crisis_message(text):
        logger.warning(
            "Message de crise détecté pour user_id=%s",
            user_id,
        )
        await message.answer(CRISIS_RESPONSE, parse_mode="Markdown")
        return

    await bot.send_chat_action(message.chat.id, "typing")

    history = await store.get_history(user_id)

    try:
        response = await get_answer(history, text)
    except AIServiceError:
        await message.answer(ERROR_OPENAI)
        return
    except Exception:
        logger.exception(
            "Erreur inattendue pour user_id=%s",
            user_id,
        )
        await message.answer(ERROR_GENERIC)
        return

    await message.answer(response)
    await message.answer(
        "Ask your next question or clear the memory:",
        reply_markup=_kb_clear_memory(),
    )
    await store.append_exchange(user_id, text, response)
    logger.info("Réponse envoyée à user_id=%s", user_id)
