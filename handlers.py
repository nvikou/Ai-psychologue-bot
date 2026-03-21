from aiogram.types import Message, BotCommand, CallbackQuery
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton as IKB
from libs import get_answer
import logging
import os
from dotenv import load_dotenv
load_dotenv()


# Промпт: психология эмоций
SYSTEM_PROMPT = f"""You are Dr. Émile, an expert clinical psychologist with 20 years of experience \.
Chat with the user \. Help the user understand and manage their emotions \.
"""

router = Router()
dict_memory = dict()  # Словарь для сохранения истории переписки


# Inline кнопка для очистки истории переписки
def kb_clear_memory():
    return InlineKeyboardMarkup(
        inline_keyboard=[[IKB(text="🗑️ Effacer l'historique",
                              callback_data="clear_memory")]])


# Функция очистки истории переписки по id пользователя
async def clear_memory(tg_id):
    try:
        global dict_memory
        dict_memory[tg_id] = ''
        mem = dict_memory[tg_id]
        logging.info(f'Очистка истории переписки ({tg_id}) {mem}')
    except:
        logging.error('clear_memory()')


# Обработка нажатия на кнопку - очистка истории переписки
@router.callback_query(F.data == "clear_memory")
async def handle_clear_callback(callback: CallbackQuery):
    await clear_memory(callback.from_user.id)
    # await callback.message.edit_reply_markup(reply_markup=None) # удаление кнопки после нажатия
    # удаление кнопки с текстом над кнопкой (последнее сообщение)
    await callback.message.delete()


# Меню бота
@router.startup()
async def set_menu_button(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Start')]
    await bot.set_my_commands(main_menu_commands)


# Обработка команды /start
@router.message(Command('start'))
async def cmd_start(message: Message):
    await clear_memory(message.from_user.id)
    await message.answer(
        " Bonjour mon ami, je suis un psychologue expérimenté. En quoi t'aider? 🧠"
    )


# Обработка текстового сообщения от пользователя
@router.message(F.text)
async def handle_dialog(message: Message):
    logging.info(
        f"handle_dialog() - Запрос от {message.from_user.id}: {message.text}")
    global dict_memory
    if message.from_user.id not in dict_memory:
        dict_memory[message.from_user.id] = ''
    history = dict_memory.get(message.from_user.id, '')

    # Запрос к OpenAI
    response = await get_answer(SYSTEM_PROMPT, history, message.text)

    await message.answer(response)
    await message.answer("Posez votre prochaine question ou effacez la mémoire :",
                         reply_markup=kb_clear_memory())

    logging.info(
        f"handle_dialog - Ответ: {message.from_user.id} отправлен")
    # запись диалога в историю
    dict_memory[message.from_user.id] += \
        f"\n\nЗапрос пользователя: {message.text}\n\nОтвет: \n{response}"
