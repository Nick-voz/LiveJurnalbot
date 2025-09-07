from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import ParametrStates
from src.bot.constants.user_data_keys import UDK
from src.bot.hendlers.base import unexpected_err_handler
from src.db.models import Parametr
from src.db.models import UserScenario
from src.db.repository import find_or_create_parametr
from src.db.repository import find_user_scenario_by_name
from src.db.repository import get_user_scenarios_by_chat


async def start_create_parametr_conv(update: Update, _) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)
    replay_text = f"choose users scenario {[e.scenario.name for e in user_scenarios]}"
    await update.message.reply_text(replay_text)
    return ParametrStates.USER_SCENARIO


async def choose_user_scenario(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = update.message.text
    chat_id = update.effective_chat.id
    user_scenio = find_user_scenario_by_name(name, chat_id)

    if user_scenio is None:
        await update.message.reply_text("try again")
        return ParametrStates.USER_SCENARIO

    await update.message.reply_text(f"name for the parametr")

    context.user_data[UDK.USER_SCENARIO] = user_scenio

    return ParametrStates.NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    scenario: UserScenario = context.user_data.get(UDK.USER_SCENARIO)
    if scenario is None:
        await update.message.reply_text("something want wrong")
        return END

    try:
        name = update.message.text
    except ValueError:
        return ParametrStates.NAME

    await update.message.reply_text(f"send default value for the parametr")

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
    await update.message.reply_text(f"success")

    return END


start_strategy_conv_hendler = CommandHandler("set_parametr", start_create_parametr_conv)
choose_user_scenario_hendler = MessageHandler(filters.TEXT, choose_user_scenario)
get_name_hendler = MessageHandler(filters.TEXT, get_name)
get_default_hendler = MessageHandler(filters.TEXT, get_default_value)


def register(app: Application):
    app.add_handler(
        ConversationHandler(
            entry_points=(start_strategy_conv_hendler,),
            states={
                ParametrStates.USER_SCENARIO: (choose_user_scenario_hendler,),
                ParametrStates.NAME: (get_name_hendler,),
                ParametrStates.DEFAULT_VALUE: (get_default_hendler,),
            },
            fallbacks=(unexpected_err_handler,),
        )
    )
