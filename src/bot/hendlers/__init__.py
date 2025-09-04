from telegram.ext import Application

from src.bot.hendlers.base import register as base_register
from src.bot.hendlers.scenarios import register as scenarios_register


def register(app: Application):
    base_register(app)
    scenarios_register(app)
