from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes

from src.bot.constants.commands_text import CMD
from src.bot.handlers.base import prepare_scenarios_list
from src.bot.handlers.base import send_menu


async def send_scenarios_list(update: Update) -> None:
    chat_id = update.effective_chat.id
    reply_text, reply_markup = prepare_scenarios_list(chat_id)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            reply_text, reply_markup=reply_markup
        )
    elif update.message:
        await update.message.reply_text(reply_text, reply_markup=reply_markup)
    else:
        raise ValueError("Update must have either callback_query or message")


async def get_my_scenarios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await send_scenarios_list(update)


async def back_to_scenarios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await send_scenarios_list(update)


async def back_to_menu(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await send_menu(update, _)


# Builders for handlers
def build_get_my_scenarios_handler():
    return CallbackQueryHandler(get_my_scenarios, pattern=rf"^{CMD.SCENARIOS_LIST}$")


def build_back_to_scenarios_handler():
    return CallbackQueryHandler(back_to_scenarios, pattern=rf"^{CMD.BACK_TO_SCENARIOS}$")


def build_back_to_menu_handler():
    return CallbackQueryHandler(back_to_menu, pattern=rf"^{CMD.MENU}$")
