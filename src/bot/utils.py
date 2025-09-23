from typing import Iterable

from itertools import batched
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import ScenariosList
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


def generate_inline_keyboard_scenarios(
    scenarios: Iterable[UserScenario],
) -> InlineKeyboardMarkup:
    keybord = []
    for batch in batched(scenarios, 3):
        buttons_batch = []
        for e in batch:
            name = e.scenario.name
            _id = e.id
            buttons_batch.append(
                InlineKeyboardButton(
                    f"{name}", callback_data=f"{ScenariosList.SCENARIO}@{_id}"
                )
            )
        keybord.append(buttons_batch)

    keybord.append(
        [
            InlineKeyboardButton(
                "Back", callback_data=f"{ScenariosList.SCENARIO}@{CMD.MENU}"
            ),
            InlineKeyboardButton(
                text="Add scenario",
                callback_data=f"{ScenariosList.SCENARIO}@{CMD.CREATE_SCENARIO}",
            ),
        ]
    )

    return InlineKeyboardMarkup(keybord)


def generate_inline_keyboard_scenario_options() -> InlineKeyboardMarkup:
    keyboard = []

    keyboard.append(
        [InlineKeyboardButton("back", callback_data=ScenariosList.SCENARIO)]
    )

    return InlineKeyboardMarkup(keyboard)
