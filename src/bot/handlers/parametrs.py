from typing import Any

from sqlalchemy.orm import keyfunc_mapping
from telegram import Update
from telegram.ext import Application
from telegram.ext import BaseHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import ParameterStates
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.base import prepare_scenarios_list
from src.bot.keyboards.parametrs import get_continue_keyboard
from src.bot.keyboards.scenarios import get_keyboard_scenarios
from sqlalchemy.orm import Session

from src.db.models import Parameter
from src.db.models import UserScenario
from src.db.models import engine
from src.db.repository import find_or_create_parameter
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenarios_by_chat

# Utility functions


def validate_param_name(text: str) -> str | None:
    cleaned = text.strip()
    return cleaned if cleaned else None


def validate_and_set_default_value(text: str, parameter: Parameter) -> bool:
    try:
        value = float(text)
        if not 0 <= value <= 1000:
            return False
        parameter.default_value = value
        return True
    except ValueError:
        return False


async def start_create_parameter_conv(update: Update, _) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)

    reply_markup = get_keyboard_scenarios(user_scenarios)

    await update.message.reply_text("Select scenario", reply_markup=reply_markup)
    return ParametrStates.USER_SCENARIO


async def start_direct_parameter_conv(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    scenario = context.user_data.get(UDK.USER_SCENARIO_ID)
    if scenario is None:
        await update.message.reply_text(
            "No scenario selected. Please use /set_parameter first to select a scenario."
        )
        return END

    await update.message.reply_text("Send name for the parameter")
    return ParameterStates.NAME


async def choose_user_scenario(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    user_scenario = get_user_scenario_by_id(query.data)

    if user_scenario is None:
        await query.message.reply_text("Scenario not found. Please select again.")
        return ParameterStates.USER_SCENARIO

    await query.edit_message_text("Send name for the parameter")
    context.user_data[UDK.USER_SCENARIO_ID] = user_scenario

    return ParameterStates.NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    scenario: UserScenario = context.user_data.get(UDK.USER_SCENARIO_ID)
    if scenario is None:
        await update.message.reply_text(
            "An error occurred. Please restart the process."
        )
        return END

    param_name = validate_param_name(update.message.text)
    if param_name is None:
        await update.message.reply_text("Invalid name. Please enter a non-empty name.")
        return ParameterStates.NAME

    await update.message.reply_text("Send default value for the parameter")

    parameter = find_or_create_parameter(scenario, param_name)
    context.user_data[UDK.PARAMETER] = parameter

    return ParameterStates.DEFAULT_VALUE


async def get_default_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parameter: Parameter = context.user_data.get(UDK.PARAMETER)
    if parameter is None:
        await update.message.reply_text(
            "An error occurred. Please restart the process."
        )
        return END

    if not validate_and_set_default_value(update.message.text, parameter):
        await update.message.reply_text(
            "Invalid value. Please enter a number between 0 and 1000."
        )
        return ParameterStates.DEFAULT_VALUE

    with Session(engine) as s:
        s.add(parameter)
        s.commit()
    await update.message.reply_text(
        "Parameter created successfully. Do you want to add another parameter?",
        reply_markup=get_continue_keyboard(),
    )

    return ParameterStates.CONTINUE


async def handle_continue(update: Update, _) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == CMD.CONFIRM:
        await query.edit_message_text("Send name for the parameter")
        return ParameterStates.NAME
    if query.data == CMD.DENY:
        await query.edit_message_text("Parameter creation finished.")
        message, keyboard = prepare_scenarios_list(update.effective_chat.id)
        await update.effective_chat.send_message(message, reply_markup=keyboard)
        return END
    await query.edit_message_text("Invalid choice. Please try again.")
    return ParameterStates.CONTINUE


# Builders for individual handlers


def build_start_parameter_command_handler():
    return CommandHandler("set_parameter", start_create_parameter_conv)


def build_choose_user_scenario_handler():
    return CallbackQueryHandler(choose_user_scenario)


def build_name_text_handler():
    return MessageHandler(filters.TEXT, get_name)


def build_default_value_text_handler():
    return MessageHandler(filters.TEXT, get_default_value)


def build_continue_handler():
    return CallbackQueryHandler(
        handle_continue, pattern=f"^({CMD.CONFIRM}|{CMD.DENY})$"
    )


def build_parameter_conversation_handler():
    return ConversationHandler(
        entry_points=(build_start_parameter_command_handler(),),
        states={
            ParameterStates.USER_SCENARIO: (build_choose_user_scenario_handler(),),
            ParameterStates.NAME: (build_name_text_handler(),),
            ParameterStates.DEFAULT_VALUE: (build_default_value_text_handler(),),
            ParameterStates.CONTINUE: (build_continue_handler(),),
        },
        fallbacks=(build_cancel_handler(), build_unexpected_err_handler()),
    )


def build_direct_conversation_handler(
    entry_points: list[BaseHandler[Update, Any, object]],
    map_to_parent: dict[object, object],
):
    return ConversationHandler(
        entry_points=entry_points or [build_name_text_handler()],
        states={
            ParameterStates.NAME: (build_name_text_handler(),),
            ParameterStates.DEFAULT_VALUE: (build_default_value_text_handler(),),
            ParameterStates.CONTINUE: (build_continue_handler(),),
        },
        fallbacks=(build_cancel_handler(), build_unexpected_err_handler()),
        map_to_parent=map_to_parent or {END: END},
    )


def register(app: Application):
    app.add_handler(build_parameter_conversation_handler())
