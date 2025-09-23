from sqlalchemy.engine.interfaces import SchemaTranslateMapType
from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import Menu
from src.bot.constants.conversation_states import Scenario
from src.bot.constants.conversation_states import ScenariosList
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import cancel_handler
from src.bot.handlers.base import send_menu
from src.bot.handlers.base import unexpected_err_handler
from src.bot.utils import generate_inline_keyboard_scenario_options
from src.bot.utils import generate_inline_keyboard_scenarios
from src.db.repository import create_user_scenario
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenarios_by_chat


async def get_my_scenarios(update: Update, _) -> int:
    await update.callback_query.answer()
    chat_id = update.callback_query.message.chat.id
    scenarios = get_user_scenarios_by_chat(chat_id)

    reply_text = "Chose scenario to interact or tup back to menu."
    reply_markup = generate_inline_keyboard_scenarios(scenarios)

    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

    return ScenariosList.SCENARIO


async def choose_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update.callback_query.answer()
    text = update.callback_query.data.split("@")[1]

    if CMD.MENU in text:
        await send_menu(update, context)
        return END

    try:
        scenario_id = int(text)
    except ValueError:
        return get_my_scenarios(update, context)

    scenorio = get_user_scenario_by_id(scenario_id)
    context.user_data[UDK.USER_SCENARIO] = scenorio

    reply_text = f"Chose option for scenario: {scenorio.scenario.name}"
    reply_markup = generate_inline_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup)

    return ScenariosList.OPTION


async def create_scenario(update: Update, _) -> int:
    await update.callback_query.answer()
    reply_text = "Into next message send the scenario name."
    await update.callback_query.edit_message_text(reply_text)
    return Scenario.NAME


async def get_scenario_name(update: Update, _) -> int:
    chat_id = update.effective_chat.id
    name = update.message.text
    create_user_scenario(chat_id=chat_id, name=name)
    await update.message.reply_text(
        f"scenario with name: '{name}' was added to your scenarios"
    )
    await send_menu(update, _)
    return END


create_scenario_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            create_scenario, pattern=f"{ScenariosList.SCENARIO}@{CMD.CREATE_SCENARIO}"
        )
    ],
    states={
        Scenario.NAME: [MessageHandler(filters.TEXT, get_scenario_name)],
    },
    fallbacks=[cancel_handler, unexpected_err_handler],
    map_to_parent={END: END},
)

scenarios_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            get_my_scenarios, pattern="^" + str(CMD.SCENARIOS_LIST) + "$"
        )
    ],
    states={
        ScenariosList.SCENARIO: [
            CallbackQueryHandler(
                choose_scenario, pattern=rf"^{ScenariosList.SCENARIO}@(\d*|{CMD.MENU})$"
            ),
            create_scenario_conv_handler,
        ],
    },
    fallbacks=[cancel_handler, unexpected_err_handler],
    map_to_parent={END: Menu.CHOOSING_OPTION},
)
