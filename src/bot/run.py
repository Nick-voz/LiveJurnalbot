import os

from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

TOKEN = os.getenv("BOT_TOKEN")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", hello))


def run_bot():
    app.run_polling()
