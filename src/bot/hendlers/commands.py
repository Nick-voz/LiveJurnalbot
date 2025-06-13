from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

from src.templates.env import env


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_text = env.get_template("greeting.txt").render(
        name=update.effective_chat.first_name
    )
    await update.message.reply_text(reply_text)


def register(app: Application):
    app.add_handler(CommandHandler("start", hello))
