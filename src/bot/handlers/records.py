from zoneinfo import ZoneInfo

from datetime import datetime
from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
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
from src.bot.keyboards.scenarios import get_keyboard_scenario_options
from src.bot.keyboards.scenarios import get_keyboard_scenarios
from src.db.models import Parameter
from src.db.models import Record
from src.db.models import engine
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenario_parameters
from src.db.repository import get_user_scenarios_by_chat

# Core async handlers (unchanged logic)


async def start_add_record_conv(update: Update, _) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)

    reply_markup = get_keyboard_scenarios(user_scenarios)

    await update.message.reply_text("Select scenario", reply_markup=reply_markup)
    return RecordStates.USER_SCENARIO


async def choose_user_scenario(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    scenario_id = query.data
    user_scenario = get_user_scenario_by_id(scenario_id)
    if user_scenario is None:
        return RecordStates.USER_SCENARIO

    parameters = get_user_scenario_parameters(user_scenario)
    if not parameters:
        await query.edit_message_text("No parameters in this scenario.")
        return END

    context.user_data[UDK.USER_SCENARIO_ID] = user_scenario
    context.user_data[UDK.PARAMETERS] = parameters
    context.user_data[UDK.CURRENT_PARAM_INDEX] = 0
    parameter = parameters[0]
    await query.edit_message_text(f"Send value for parameter: {parameter.name}")
    context.user_data[UDK.PARAMETER] = parameter
    return RecordStates.VALUE


async def get_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parameter: Parameter = context.user_data.get(UDK.PARAMETER)
    record = Record(
        parameter_id=parameter.id, datetime=datetime.now(tz=ZoneInfo("Europe/Moscow"))
    )

    try:
        record.value = update.message.text
    except ValueError:
        await update.message.reply_text("can not recognize value, try again")
        return RecordStates.VALUE

    with Session(engine) as s:
        s.add(record)
        s.commit()
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


# Builders for handlers


def build_start_add_record_command_handler():
    return CommandHandler(CMD.CREATE_RECORD, start_add_record_conv)


def build_choose_user_scenario_handler():
    return CallbackQueryHandler(choose_user_scenario)


def build_get_value_handler():
    return MessageHandler(filters.TEXT, get_value)


def build_conversation_handler():
    return ConversationHandler(
        entry_points=(build_start_add_record_command_handler(),),
        states={
            RecordStates.USER_SCENARIO: (build_choose_user_scenario_handler(),),
            RecordStates.VALUE: (build_get_value_handler(),),
        },
        fallbacks=(build_cancel_handler(), build_unexpected_err_handler()),
    )
