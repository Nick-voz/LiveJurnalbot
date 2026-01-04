from typing import Iterable

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from src.bot.constants.commands_text import CMD
from src.db.models import Parameter


def get_keyboard_parameters(
    parameters: Iterable[Parameter],
) -> InlineKeyboardMarkup:
    keyboard = []
    for e in parameters:
        name = e.name
        keyboard.append((InlineKeyboardButton(f"{name}", callback_data=name),))

    return InlineKeyboardMarkup(keyboard)


def get_continue_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=CMD.CONFIRM),
            InlineKeyboardButton("No", callback_data=CMD.DENY),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
