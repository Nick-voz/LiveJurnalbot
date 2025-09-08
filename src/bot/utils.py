from typing import Iterable

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from src.db.models import Parametr
from src.db.models import UserScenario


def generate_inline_keyboard_user_scenarios(
    user_scenarios: Iterable[UserScenario],
) -> InlineKeyboardMarkup:
    keybord = []
    for e in user_scenarios:
        name = e.scenario.name
        keybord.append((InlineKeyboardButton(f"{name}", callback_data=name),))

    return InlineKeyboardMarkup(keybord)


def generate_inline_keyboard_parametrs(
    parametrs: Iterable[Parametr],
) -> InlineKeyboardMarkup:
    keybord = []
    for e in parametrs:
        name = e.name
        keybord.append((InlineKeyboardButton(f"{name}", callback_data=name),))

    return InlineKeyboardMarkup(keybord)
