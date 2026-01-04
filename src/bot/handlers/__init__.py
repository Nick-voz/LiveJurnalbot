from telegram.ext import Application

from src.bot.handlers.menu import register as menu_register
from src.bot.handlers.parametrs import register as parameters_register
from src.bot.handlers.reminder_strategies import (
    register as reminder_strategies_register,
)


def register(app: Application):
    reminder_strategies_register(app)
    parameters_register(app)
    menu_register(app)
