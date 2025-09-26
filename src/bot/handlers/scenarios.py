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
from src.bot.keyboards.scenarios import get_keyboard_scenario_options
from src.bot.keyboards.scenarios import get_keyboard_scenarios
from src.db.repository import create_user_scenario
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenarios_by_chat


async def get_my_scenarios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    chat_id = update.callback_query.message.chat.id
    scenarios = get_user_scenarios_by_chat(chat_id)

    reply_text = "Chose scenario to interact or tup back to menu."
    reply_markup = get_keyboard_scenarios(scenarios)

    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

    return ScenariosList.SCENARIO


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update.callback_query.answer()
    await send_menu(update, context)
    return END


async def choose_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    scenario_id = int(update.callback_query.data)
    context.user_data[UDK.USER_SCENARIO_ID] = scenario_id
    scenario = get_user_scenario_by_id(scenario_id)

    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

    await update.callback_query.answer()
    return ScenariosList.OPTION


async def choose_option(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await send_menu(update, _)
    await update.callback_query.answer()
    return END


async def create_scenario(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    reply_text = "Into next message send the scenario name."
    await update.callback_query.edit_message_text(reply_text)
    return Scenario.NAME


async def get_scenario_name(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    name = update.message.text
    create_user_scenario(chat_id=chat_id, name=name)
    await update.message.reply_text(
        f"scenario with name: '{name}' was added to your scenarios"
    )
    await send_menu(update, _)
    return END


# Builders (factory-style constructors) for handlers


def build_get_my_scenarios_handler():
    return CallbackQueryHandler(get_my_scenarios, pattern=rf"^{CMD.SCENARIOS_LIST}$")


def build_back_handler():
    return CallbackQueryHandler(back, pattern=rf"^{CMD.MENU}$")


def build_choose_scenario_handler():
    return CallbackQueryHandler(choose_scenario, pattern=r"^\d*$")


def build_choose_option_handler():
    return CallbackQueryHandler(choose_option, pattern=r"^bruh$")


def build_create_scenario_handler():
    # Entry point and nested state machine for creating a scenario
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(create_scenario, pattern=CMD.CREATE_SCENARIO)
        ],
        states={
            Scenario.NAME: [MessageHandler(filters.TEXT, get_scenario_name)],
        },
        fallbacks=[cancel_handler, unexpected_err_handler],
        map_to_parent={END: END},
    )


# Top-level builders for the full conversation handlers


def build_scenarios_handler():
    create_scenario_conv_handler = build_create_scenario_handler()

    return ConversationHandler(
        entry_points=[build_get_my_scenarios_handler()],
        states={
            ScenariosList.SCENARIO: [
                build_choose_scenario_handler(),
                build_back_handler(),
                create_scenario_conv_handler,
            ],
            ScenariosList.OPTION: [
                build_choose_option_handler(),
            ],
        },
        fallbacks=[cancel_handler, unexpected_err_handler],
        map_to_parent={END: Menu.CHOOSING_OPTION},
    )


create_scenario_conv_handler = build_create_scenario_handler()

scenarios_handler = build_scenarios_handler()
