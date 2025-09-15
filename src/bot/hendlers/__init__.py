from telegram.ext import Application

from src.bot.hendlers.menu import register as menu_register
from src.bot.hendlers.parametrs import register as parametrs_register
from src.bot.hendlers.records import register as records_register
from src.bot.hendlers.reminder_strategies import (
    register as reminder_strategies_register,
)
from src.bot.hendlers.scenarios import register as scenarios_register


def register(app: Application):
    scenarios_register(app)
    reminder_strategies_register(app)
    parametrs_register(app)
    records_register(app)
    menu_register(app)
