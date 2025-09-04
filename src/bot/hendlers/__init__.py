from telegram.ext import Application

from src.bot.hendlers.base import register as base_register


def register(app: Application):
    base_register(app)
