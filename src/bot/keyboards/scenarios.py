from typing import Iterable

from itertools import batched
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from src.bot.constants.commands_text import CMD
from src.db.models import UserScenario


def get_keyboard_scenarios(
    scenarios: Iterable[UserScenario],
) -> InlineKeyboardMarkup:
    keybord = []
    for batch in batched(scenarios, 3):
        buttons_batch = []
        for e in batch:
            name = e.scenario.name
            _id: int = e.id
            buttons_batch.append(InlineKeyboardButton(name, callback_data=str(_id)))
        keybord.append(buttons_batch)

    keybord.append(
        [
            InlineKeyboardButton("Back", callback_data=CMD.MENU),
            InlineKeyboardButton(
                "Add scenario",
                callback_data=CMD.CREATE_SCENARIO,
            ),
        ]
    )

    return InlineKeyboardMarkup(keybord)


def get_keyboard_scenario_options() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Delete", callback_data=CMD.DELETE_SCENARIO),
            InlineKeyboardButton("Fill (Add Record)", callback_data=CMD.FILL_SCENARIO),
        ],
        [
            InlineKeyboardButton("Edit", callback_data=CMD.EDIT_SCENARIO),
            InlineKeyboardButton("Back", callback_data=CMD.MENU),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_keyboard_delete_confirmation() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=CMD.CONFIRM),
            InlineKeyboardButton("No", callback_data=CMD.DENY),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
