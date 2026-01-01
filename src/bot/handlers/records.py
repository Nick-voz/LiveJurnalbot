from zoneinfo import ZoneInfo

from datetime import datetime
from telegram import Update
from telegram.ext import Application
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
from src.bot.keyboards.scenarios import get_keyboard_scenarios
from src.db.models import Parametr
from src.db.models import Record
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenario_parametrs
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

    parametrs = get_user_scenario_parametrs(user_scenario)
    if not parametrs:
        await query.edit_message_text("No parameters in this scenario.")
        return END

    context.user_data[UDK.USER_SCENARIO_ID] = user_scenario
    context.user_data[UDK.PARAMETERS] = parametrs
    context.user_data[UDK.CURRENT_PARAM_INDEX] = 0
    parametr = parametrs[0]
    await query.edit_message_text(f"Send value for parameter: {parametr.name}")
    context.user_data[UDK.PARAMETR] = parametr
    return RecordStates.VALUE


async def get_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parametr: Parametr = context.user_data.get(UDK.PARAMETR)
    record = Record(
        parameter_id=parametr.id, datetime=datetime.now(tz=ZoneInfo("Europe/Moscow"))
    )

    try:
        record.value = float(update.message.text)
    except ValueError:
        await update.message.reply_text("can not recognize value, try again")
        return RecordStates.VALUE

    record.save()
    await update.message.reply_text("success")

    index = context.user_data.get(UDK.CURRENT_PARAM_INDEX, 0)
    parameters = context.user_data.get(UDK.PARAMETERS, [])
    index += 1
    if index < len(parameters):
        context.user_data[UDK.CURRENT_PARAM_INDEX] = index
        parametr = parameters[index]
        context.user_data[UDK.PARAMETR] = parametr
        await update.message.reply_text(f"Send value for parameter: {parametr.name}")
        return RecordStates.VALUE

    await update.message.reply_text("All values recorded successfully.")
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


# Public registrar


def register(app: Application):
    app.add_handler(build_conversation_handler())
