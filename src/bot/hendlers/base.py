from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.db.repository import create_user
from src.db.repository import get_user_by_chat
from src.templates.env import env


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user = get_user_by_chat(chat_id)
    if user is None:
        create_user(chat_id)
        user = get_user_by_chat(chat_id)

    reply_text = env.get_template("greeting.txt").render(
        name=update.effective_chat.first_name
    )
    await update.message.reply_text(reply_text)


async def unexpected_err(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("unexpected err")


start_cmd_handler = CommandHandler("start", hello)
unexpected_err_handler = MessageHandler(filters.ALL, unexpected_err)


def register(app: Application):
    app.add_handlers((start_cmd_handler,))
