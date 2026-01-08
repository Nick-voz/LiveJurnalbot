from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes

from src.bot.constants.commands_text import CMD
from src.bot.handlers.base import prepare_scenarios_list


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


# Builder for handler
def build_get_my_scenarios_handler():
    return CallbackQueryHandler(get_my_scenarios, pattern=rf"^{CMD.SCENARIOS_LIST}$")
