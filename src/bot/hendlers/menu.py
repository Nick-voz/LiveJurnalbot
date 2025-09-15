from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import Base
from src.bot.hendlers.base import cancel_hendler
from src.bot.hendlers.base import send_menu
from src.bot.hendlers.base import unexpected_err_handler
from src.bot.hendlers.scenarios import create_scenario_conv_hendler
from src.db.repository import create_user
from src.db.repository import get_user_by_chat


def remember_user_if_not_yet(chat_id: int) -> None:
    user = get_user_by_chat(chat_id)
    if user is None:
        create_user(chat_id)
        user = get_user_by_chat(chat_id)


async def hello(update: Update, _) -> int:
    remember_user_if_not_yet(update.effective_chat.id)
    await send_menu(update, _)
    return Base.CHOOSING_OPTION


start_cmd_handler = CommandHandler(CMD.START, hello)
menu_hendler = ConversationHandler(
    entry_points=[start_cmd_handler],
    states={Base.CHOOSING_OPTION: [create_scenario_conv_hendler]},
    fallbacks=[cancel_hendler, unexpected_err_handler],
)


def register(app: Application):
    app.add_handler(menu_hendler)
