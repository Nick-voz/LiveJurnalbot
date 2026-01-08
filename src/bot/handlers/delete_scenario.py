from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import ScenariosList
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.scenarios_list import send_scenarios_list
from src.bot.keyboards.scenarios import get_keyboard_delete_confirmation
from src.bot.keyboards.scenarios import get_keyboard_scenario_options
from src.db.repository import delete_user_scenario_by_id
from src.db.repository import get_user_scenario_by_id


async def delete_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    scenario = get_user_scenario_by_id(scenario_id)
    reply_text = f"Are you sure you want to delete scenario '{scenario.scenario.name}'?"
    reply_markup = get_keyboard_delete_confirmation()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)
    return ScenariosList.DELETE_CONFIRM


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    delete_user_scenario_by_id(scenario_id)
    await send_scenarios_list(update)
    return END


async def cancel_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    scenario = get_user_scenario_by_id(scenario_id)
    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)
    return END


# Builders for handlers
def build_delete_scenario_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_scenario, pattern=rf"^{CMD.DELETE_SCENARIO}$")
        ],
        states={
            ScenariosList.DELETE_CONFIRM: [
                CallbackQueryHandler(confirm_delete, pattern=rf"^{CMD.CONFIRM}$"),
                CallbackQueryHandler(cancel_delete, pattern=rf"^{CMD.DENY}$"),
            ],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={END: END},
    )
