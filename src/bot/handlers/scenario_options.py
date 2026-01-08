from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes

from src.bot.constants.commands_text import CMD
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.scenarios_list import send_scenarios_list
from src.bot.keyboards.scenarios import get_keyboard_scenario_options
from src.db.repository import get_user_scenario_by_id


async def choose_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    scenario_id = int(update.callback_query.data)
    context.user_data[UDK.USER_SCENARIO_ID] = scenario_id
    scenario = get_user_scenario_by_id(scenario_id)

    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

    await update.callback_query.answer()


async def back_to_scenarios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await send_scenarios_list(update)


async def back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    scenario = get_user_scenario_by_id(scenario_id)
    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)


# Builders for handlers
def build_choose_scenario_handler():
    return CallbackQueryHandler(choose_scenario, pattern=r"^\d*$")


def build_back_to_scenarios_handler():
    return CallbackQueryHandler(
        back_to_scenarios, pattern=rf"^{CMD.BACK_TO_SCENARIOS}$"
    )


def build_back_to_options_handler():
    return CallbackQueryHandler(back_to_options, pattern=rf"^{CMD.BACK_TO_OPTIONS}$")
