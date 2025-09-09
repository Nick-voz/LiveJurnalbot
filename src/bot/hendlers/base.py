from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.db.repository import create_user
from src.db.repository import get_user_by_chat
from src.templates.env import env


async def hello(update: Update, _) -> None:
    chat_id = update.effective_chat.id
    user = get_user_by_chat(chat_id)
    if user is None:
        create_user(chat_id)
        user = get_user_by_chat(chat_id)

    reply_text = env.get_template("greeting.txt").render(
        name=update.effective_chat.first_name
    )
    await update.message.reply_text(reply_text)


async def unexpected_err(update: Update, _) -> None:
    await update.message.reply_text("unexpected err")


async def cancel(update: Update, _) -> int:
    await update.message.reply_text("conv canceled")
    return END


start_cmd_handler = CommandHandler(CMD.START, hello)
unexpected_err_handler = MessageHandler(filters.ALL, unexpected_err)
cancel_hendler = CommandHandler(CMD.CANCEL, cancel)


def register(app: Application):
    app.add_handlers((start_cmd_handler,))
