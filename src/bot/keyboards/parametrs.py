from typing import Iterable

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from src.db.models import Parametr


def get_keyboard_parametrs(
    parametrs: Iterable[Parametr],
) -> InlineKeyboardMarkup:
    keybord = []
    for e in parametrs:
        name = e.name
        keybord.append((InlineKeyboardButton(f"{name}", callback_data=name),))

    return InlineKeyboardMarkup(keybord)
