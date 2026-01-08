from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import RecordStates
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.records import build_get_value_handler
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenario_parameters


async def fill_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    user_scenario = get_user_scenario_by_id(scenario_id)
    parameters = get_user_scenario_parameters(user_scenario)
    if not parameters:
        await update.callback_query.edit_message_text("No parameters in this scenario.")
        return END
    context.user_data[UDK.PARAMETERS] = parameters
    context.user_data[UDK.CURRENT_PARAM_INDEX] = 0
    parameter = parameters[0]
    await update.callback_query.edit_message_text(
        f"Send value for parameter: {parameter.name}"
    )
    context.user_data[UDK.PARAMETER] = parameter
    return RecordStates.VALUE


# Builder for handler
def build_fill_scenario_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(fill_scenario, pattern=rf"^{CMD.FILL_SCENARIO}$")
        ],
        states={
            RecordStates.VALUE: [build_get_value_handler()],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={
            END: END
        },  # Assuming back to options, but since separate, perhaps to a state
    )
