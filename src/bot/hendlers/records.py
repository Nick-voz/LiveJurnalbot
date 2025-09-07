from zoneinfo import ZoneInfo

from datetime import datetime
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import ParametrStates
from src.bot.constants.conversation_states import RecordStates
from src.bot.constants.user_data_keys import UDK
from src.bot.hendlers.base import unexpected_err_handler
from src.db.models import Parametr
from src.db.models import Record
from src.db.repository import find_user_scenario_by_name
from src.db.repository import get_user_scenario_parametrs
from src.db.repository import get_user_scenarios_by_chat


async def start_add_record_conv(update: Update, _) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)

    keybord = [[]]
    for e in user_scenarios:
        name = e.scenario.name
        keybord[0].append(InlineKeyboardButton(f"{name}", callback_data=name))

    reply_markup = InlineKeyboardMarkup(keybord)

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

    keybord = [[]]
    for e in parametrs:
        name = e.name
        keybord[0].append(InlineKeyboardButton(f"{name}", callback_data=name))

    reply_markup = InlineKeyboardMarkup(keybord)

    await query.edit_message_text("choose parametr", reply_markup=reply_markup)

    context.user_data[UDK.USER_SCENARIO] = user_scenio

    return ParametrStates.NAME


async def choose_parametr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_scenio = context.user_data.get(UDK.USER_SCENARIO)
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
        await update.message.reply_text("can not find parametr with this name")

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


start_add_record_conv_hendler = CommandHandler("add_record", start_add_record_conv)
choose_user_scenario_hendler = CallbackQueryHandler(choose_user_scenario)
choose_parametr_hendler = CallbackQueryHandler(choose_parametr)
get_value_hendler = MessageHandler(filters.TEXT, get_value)


def register(app: Application):
    app.add_handler(
        ConversationHandler(
            entry_points=(start_add_record_conv_hendler,),
            states={
                RecordStates.USER_SCENARIO: (choose_user_scenario_hendler,),
                RecordStates.PARAMETR: (choose_parametr_hendler,),
                RecordStates.VALUE: (get_value_hendler,),
            },
            fallbacks=(unexpected_err_handler,),
        )
    )
