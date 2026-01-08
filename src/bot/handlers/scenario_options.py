from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes

from src.bot.constants.commands_text import CMD
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import display_scenario_options
from src.bot.handlers.scenarios_list import send_scenarios_list


async def choose_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    scenario_id = int(update.callback_query.data)
    context.user_data[UDK.USER_SCENARIO_ID] = scenario_id
    await display_scenario_options(update, context, scenario_id)
    await update.callback_query.answer()


async def back_to_scenarios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await send_scenarios_list(update)


async def back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    await display_scenario_options(update, context, scenario_id)


# Builders for handlers
def build_choose_scenario_handler():
    return CallbackQueryHandler(choose_scenario, pattern=r"^\d*$")


def build_back_to_scenarios_handler():
    return CallbackQueryHandler(
        back_to_scenarios, pattern=rf"^{CMD.BACK_TO_SCENARIOS}$"
    )


def build_back_to_options_handler():
    return CallbackQueryHandler(back_to_options, pattern=rf"^{CMD.BACK_TO_OPTIONS}$")
