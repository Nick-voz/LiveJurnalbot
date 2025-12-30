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
from src.bot.constants.conversation_states import ParametrStates
from src.bot.constants.conversation_states import RecordStates
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import cancel_handler
from src.bot.handlers.base import unexpected_err_handler
from src.bot.keyboards.parametrs import get_keyboard_parametrs
from src.bot.keyboards.scenarios import get_keyboard_scenarios
from src.db.models import Parametr
from src.db.models import Record
from src.db.repository import find_user_scenario_by_name
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
    name = query.data
    chat_id = update.effective_chat.id
    user_scenio = find_user_scenario_by_name(name, chat_id)

    if user_scenio is None:
        return RecordStates.USER_SCENARIO

    parametrs = get_user_scenario_parametrs(user_scenio)

    reply_markup = get_keyboard_parametrs(parametrs)

    await query.edit_message_text("choose parametr", reply_markup=reply_markup)

    context.user_data[UDK.USER_SCENARIO_ID] = user_scenio

    return ParametrStates.NAME


async def choose_parametr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_scenio = context.user_data.get(UDK.USER_SCENARIO_ID)
    parametr_name = query.data

    if user_scenio is None:
        await query.message.reply_text("try again")
        return RecordStates.USER_SCENARIO

    parametrs = get_user_scenario_parametrs(user_scenio)
    try:
        parametr = next(
            (p for p in parametrs if p.name.lower() == parametr_name.lower())
        )
    except StopIteration:
        await query.message.reply_text("can not find parametr with this name")

    await query.edit_message_text("send value for parametr")
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

    return END


# Builders for handlers


def build_start_add_record_command_handler():
    return CommandHandler(CMD.CREATE_RECORD, start_add_record_conv)


def build_choose_user_scenario_handler():
    return CallbackQueryHandler(choose_user_scenario)


def build_choose_parametr_handler():
    return CallbackQueryHandler(choose_parametr)


def build_get_value_handler():
    return MessageHandler(filters.TEXT, get_value)


def build_conversation_handler():
    return ConversationHandler(
        entry_points=(build_start_add_record_command_handler(),),
        states={
            RecordStates.USER_SCENARIO: (build_choose_user_scenario_handler(),),
            RecordStates.PARAMETR: (build_choose_parametr_handler(),),
            RecordStates.VALUE: (build_get_value_handler(),),
        },
        fallbacks=(cancel_handler, unexpected_err_handler),
    )


# Public registrar


def register(app: Application):
    app.add_handler(build_conversation_handler())
