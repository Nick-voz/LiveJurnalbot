from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes

from src.bot.constants.commands_text import CMD
from src.bot.constants.user_data_keys import UDK
from src.bot.keyboards.scenarios import get_keyboard_scenario_parameters
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenario_parameters


async def show_parameters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    user_scenario = get_user_scenario_by_id(scenario_id)
    parameters = get_user_scenario_parameters(user_scenario)
    reply_text = f"Parameters for scenario '{user_scenario.scenario.name}':"
    reply_markup = get_keyboard_scenario_parameters(parameters)
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)


async def choose_parameter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Not implemented yet.")
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    user_scenario = get_user_scenario_by_id(scenario_id)
    parameters = get_user_scenario_parameters(user_scenario)
    reply_text = f"Parameters for scenario '{user_scenario.scenario.name}':"
    reply_markup = get_keyboard_scenario_parameters(parameters)
    await update.effective_chat.send_message(reply_text, reply_markup=reply_markup)


# Builders for handlers
def build_show_parameters_handler():
    return CallbackQueryHandler(show_parameters, pattern=rf"^{CMD.SHOW_PARAMETERS}$")


def build_choose_parameter_handler():
    return CallbackQueryHandler(choose_parameter, pattern=r"^param_\d+$")
