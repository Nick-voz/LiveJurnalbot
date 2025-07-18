import os

from telegram.ext import ApplicationBuilder

from src.bot.hendlers.commands import register

TOKEN = os.getenv("BOT_TOKEN")


app = ApplicationBuilder().token(TOKEN).build()


def run_bot():
    register(app)
    app.run_polling()
