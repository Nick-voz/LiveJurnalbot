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
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import cancel_handler
from src.bot.handlers.base import unexpected_err_handler
from src.bot.keyboards.scenarios import get_keyboard_scenarios
from src.db.models import Parametr
from src.db.models import UserScenario
from src.db.repository import find_or_create_parametr
from src.db.repository import find_user_scenario_by_name
from src.db.repository import get_user_scenarios_by_chat


async def start_create_parametr_conv(update: Update, _) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)

    reply_markup = get_keyboard_scenarios(user_scenarios)

    await update.message.reply_text("Select scenario", reply_markup=reply_markup)
    return ParametrStates.USER_SCENARIO


async def choose_user_scenario(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    name = query.data
    chat_id = update.effective_chat.id
    user_scenio = find_user_scenario_by_name(name, chat_id)

    if user_scenio is None:
        await query.message.reply_text("try again")
        return ParametrStates.USER_SCENARIO

    await query.edit_message_text("Send name for the parametr")
    context.user_data[UDK.USER_SCENARIO_ID] = user_scenio

    return ParametrStates.NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    scenario: UserScenario = context.user_data.get(UDK.USER_SCENARIO_ID)
    if scenario is None:
        await update.message.reply_text("something want wrong")
        return END

    try:
        name = update.message.text
    except ValueError:
        return ParametrStates.NAME

    await update.message.reply_text("send default value for the parametr")

    parametr = find_or_create_parametr(scenario, name)
    context.user_data[UDK.PARAMETR] = parametr

    return ParametrStates.DEFAULT_VALUE


async def get_default_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parametr: Parametr = context.user_data.get(UDK.PARAMETR)
    if parametr is None:
        await update.message.reply_text("something want wrong")
        return END

    try:
        parametr.default_value = float(update.message.text)
    except ValueError:
        return ParametrStates.DEFAULT_VALUE

    parametr.save()
    await update.message.reply_text("success")

    return END


# Builders for individual handlers


def build_start_parametr_command_handler():
    return CommandHandler("set_parametr", start_create_parametr_conv)


def build_choose_user_scenario_handler():
    return CallbackQueryHandler(choose_user_scenario)


def build_name_text_handler():
    return MessageHandler(filters.TEXT, get_name)


def build_default_value_text_handler():
    return MessageHandler(filters.TEXT, get_default_value)


def build_conversation_handler():
    return ConversationHandler(
        entry_points=(build_start_parametr_command_handler(),),
        states={
            ParametrStates.USER_SCENARIO: (build_choose_user_scenario_handler(),),
            ParametrStates.NAME: (build_name_text_handler(),),
            ParametrStates.DEFAULT_VALUE: (build_default_value_text_handler(),),
        },
        fallbacks=(cancel_handler, unexpected_err_handler),
    )


def register(app: Application):
    app.add_handler(build_conversation_handler())
