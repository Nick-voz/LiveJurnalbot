from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import RecordStates
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.base import start_filling_scenario
from src.bot.keyboards.scenarios import get_keyboard_scenario_options
from src.db.models import Parameter
from src.db.models import Value
from src.db.repository import get_user_scenario_by_id
from src.db.repository import save_value


async def fill_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    user_scenario = get_user_scenario_by_id(scenario_id)
    return await start_filling_scenario(update, context, user_scenario)


async def get_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parameter: Parameter = context.user_data.get(UDK.PARAMETER)
    record_id = context.user_data.get(UDK.RECORD_ID)
    value = Value(
        record_id=record_id, value=update.message.text, parameter_id=parameter.id
    )

    try:
        # Value is string, no conversion needed
        pass
    except ValueError:
        await update.message.reply_text("can not recognize value, try again")
        return RecordStates.VALUE

    value = save_value(value)
    await update.message.reply_text("success")

    index = context.user_data.get(UDK.CURRENT_PARAM_INDEX, 0)
    parameters = context.user_data.get(UDK.PARAMETERS, [])
    index += 1
    if index < len(parameters):
        context.user_data[UDK.CURRENT_PARAM_INDEX] = index
        parameter = parameters[index]
        context.user_data[UDK.PARAMETER] = parameter
        await update.message.reply_text(f"Send value for parameter: {parameter.name}")
        return RecordStates.VALUE

    await update.message.reply_text("All values recorded successfully.")
    if UDK.USER_SCENARIO_ID in context.user_data:
        scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
        scenario = get_user_scenario_by_id(scenario_id)
        reply_text = f"Chose option for scenario: {scenario.scenario.name}"
        reply_markup = get_keyboard_scenario_options()
        await update.message.reply_text(reply_text, reply_markup=reply_markup)
    return END


# Builder for handler
def build_get_value_handler():
    return MessageHandler(filters.TEXT, get_value)


def build_fill_scenario_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(fill_scenario, pattern=rf"^{CMD.FILL_SCENARIO}$")
        ],
        states={
            RecordStates.VALUE: [build_get_value_handler()],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={END: END},
    )
