from typing import Iterable

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from src.bot.constants.commands_text import CMD
from src.db.models import Parametr


def get_keyboard_parametrs(
    parametrs: Iterable[Parametr],
) -> InlineKeyboardMarkup:
    keybord = []
    for e in parametrs:
        name = e.name
        keybord.append((InlineKeyboardButton(f"{name}", callback_data=name),))

    return InlineKeyboardMarkup(keybord)


def get_continue_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=CMD.CONFIRM),
            InlineKeyboardButton("No", callback_data=CMD.DENY),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
