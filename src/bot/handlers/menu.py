from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import Menu
from src.bot.handlers.base import cancel_handler
from src.bot.handlers.base import send_menu
from src.bot.handlers.base import unexpected_err_handler
from src.bot.handlers.scenarios import scenarios_handler
from src.db.repository import create_user
from src.db.repository import get_user_by_chat


def remember_user_if_not_yet(chat_id: int) -> None:
    user = get_user_by_chat(chat_id)
    if user is None:
        create_user(chat_id)
        user = get_user_by_chat(chat_id)


async def menu(update: Update, _) -> int:
    remember_user_if_not_yet(update.effective_chat.id)
    await send_menu(update, _)
    return Menu.CHOOSING_OPTION


# Builder: create the top-level menu conversation handler
def build_menu_conversation_handler() -> ConversationHandler:
    menu_handler = CommandHandler(CMD.MENU, menu)

    return ConversationHandler(
        entry_points=[menu_handler],
        states={
            Menu.CHOOSING_OPTION: [scenarios_handler],
        },
        fallbacks=[cancel_handler, unexpected_err_handler],
    )


def register(app: Application):
    app.add_handler(build_menu_conversation_handler())
