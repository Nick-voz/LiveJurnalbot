from typing import Iterable

from itertools import batched
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from src.bot.constants.commands_text import CMD
from src.bot.constants.export_file_types import ExportFileTypes
from src.db.models import Parameter
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
            InlineKeyboardButton("Parameters", callback_data=CMD.SHOW_PARAMETERS),
        ],
        [
            InlineKeyboardButton("Rename", callback_data=CMD.RENAME_SCENARIO),
            InlineKeyboardButton("Export", callback_data=CMD.EXPORT_SCENARIO),
        ],
        [
            InlineKeyboardButton("Back", callback_data=CMD.BACK_TO_SCENARIOS),
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


def get_keyboard_scenario_parameters(
    parameters: Iterable[Parameter],
) -> InlineKeyboardMarkup:
    keyboard = []
    for batch in batched(parameters, 3):
        buttons_batch = []
        for param in batch:
            name = param.name
            buttons_batch.append(
                InlineKeyboardButton(name, callback_data=f"param_{param.id}")
            )
        keyboard.append(buttons_batch)

    keyboard.append([InlineKeyboardButton("Back", callback_data=CMD.BACK_TO_OPTIONS)])

    return InlineKeyboardMarkup(keyboard)


def get_keyboard_export_file_types() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    ExportFileTypes.CSV.value, callback_data=ExportFileTypes.CSV
                )
            ]
        ]
    )
