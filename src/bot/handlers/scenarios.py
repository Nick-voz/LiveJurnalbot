from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import Menu
from src.bot.constants.conversation_states import RecordStates
from src.bot.constants.conversation_states import Scenario
from src.bot.constants.conversation_states import ScenariosList
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.base import prepare_scenarios_list
from src.bot.handlers.base import send_menu
from src.bot.handlers.parametrs import build_direct_conversation_handler
from src.bot.handlers.records import build_get_value_handler
from src.bot.keyboards.parametrs import get_continue_keyboard
from src.bot.keyboards.scenarios import get_keyboard_delete_confirmation
from src.bot.keyboards.scenarios import get_keyboard_scenario_options
from src.bot.keyboards.scenarios import get_keyboard_scenario_parameters
from src.db.repository import create_user_scenario
from src.db.repository import delete_user_scenario_by_id
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenario_parameters
from src.db.repository import update_user_scenario_name


async def send_scenarios_list(update: Update) -> None:
    chat_id = update.effective_chat.id
    reply_text, reply_markup = prepare_scenarios_list(chat_id)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            reply_text, reply_markup=reply_markup
        )
    elif update.message:
        await update.message.reply_text(reply_text, reply_markup=reply_markup)
    else:
        raise ValueError("Update must have either callback_query or message")


async def get_my_scenarios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await send_scenarios_list(update)
    return ScenariosList.SCENARIO


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await send_menu(update, context)
    return END


async def back_to_scenarios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await send_scenarios_list(update)
    return ScenariosList.SCENARIO


async def show_parameters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    user_scenario = get_user_scenario_by_id(scenario_id)
    parameters = get_user_scenario_parameters(user_scenario)
    reply_text = f"Parameters for scenario '{user_scenario.scenario.name}':"
    reply_markup = get_keyboard_scenario_parameters(parameters)
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)
    return ScenariosList.PARAMETERS


async def back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    scenario = get_user_scenario_by_id(scenario_id)
    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)
    return ScenariosList.OPTION


async def choose_parameter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Not implemented yet.")
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    user_scenario = get_user_scenario_by_id(scenario_id)
    parameters = get_user_scenario_parameters(user_scenario)
    reply_text = f"Parameters for scenario '{user_scenario.scenario.name}':"
    reply_markup = get_keyboard_scenario_parameters(parameters)
    await update.effective_chat.send_message(reply_text, reply_markup=reply_markup)
    return ScenariosList.PARAMETERS


async def choose_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    scenario_id = int(update.callback_query.data)
    context.user_data[UDK.USER_SCENARIO_ID] = scenario_id
    scenario = get_user_scenario_by_id(scenario_id)

    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

    await update.callback_query.answer()
    return ScenariosList.OPTION


async def delete_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    scenario = get_user_scenario_by_id(scenario_id)
    reply_text = f"Are you sure you want to delete scenario '{scenario.scenario.name}'?"
    reply_markup = get_keyboard_delete_confirmation()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)
    return ScenariosList.DELETE_CONFIRM


async def fill_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    user_scenario = get_user_scenario_by_id(scenario_id)
    parameters = get_user_scenario_parameters(user_scenario)
    if not parameters:
        await update.callback_query.edit_message_text("No parameters in this scenario.")
        return END
    context.user_data[UDK.PARAMETERS] = parameters
    context.user_data[UDK.CURRENT_PARAM_INDEX] = 0
    parameter = parameters[0]
    await update.callback_query.edit_message_text(
        f"Send value for parameter: {parameter.name}"
    )
    context.user_data[UDK.PARAMETER] = parameter
    return RecordStates.VALUE


async def rename_scenario(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Send the new name for the scenario.")
    return ScenariosList.RENAME


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    delete_user_scenario_by_id(scenario_id)
    await send_scenarios_list(update)
    return ScenariosList.SCENARIO


async def cancel_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    scenario = get_user_scenario_by_id(scenario_id)
    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)
    return ScenariosList.OPTION


async def create_scenario(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    reply_text = "Into next message send the scenario name."
    await update.callback_query.edit_message_text(reply_text)
    return Scenario.NAME


async def get_scenario_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    name = update.message.text
    user_scenario = create_user_scenario(chat_id=chat_id, name=name)
    context.user_data[UDK.USER_SCENARIO_ID] = user_scenario
    await update.message.reply_text(
        f"scenario with name: '{name}' was added to your scenarios"
    )
    await update.message.reply_text(
        "Do you want to add parameters to this scenario?",
        reply_markup=get_continue_keyboard(),
    )
    return Scenario.ADD_PARAMETERS


async def get_new_scenario_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_name = update.message.text
    user_scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    update_user_scenario_name(user_scenario_id, new_name)
    await update.message.reply_text(f"Scenario renamed to '{new_name}'.")
    await send_scenarios_list(update)
    return ScenariosList.SCENARIO


async def handle_add_parameters(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == CMD.CONFIRM:
        await query.edit_message_text("Send name for the parameter")
        return Scenario.PARAMETERS
    if query.data == CMD.DENY:
        await query.edit_message_text("Scenario created. Returning to scenarios list.")
        reply_text, reply_markup = prepare_scenarios_list(update.effective_chat.id)
        await query.message.reply_text(reply_text, reply_markup=reply_markup)
        return Scenario.DENY
    await query.edit_message_text("Invalid choice. Please try again.")
    return Scenario.ADD_PARAMETERS


# Builders (factory-style constructors) for handlers


def build_get_my_scenarios_handler():
    return CallbackQueryHandler(get_my_scenarios, pattern=rf"^{CMD.SCENARIOS_LIST}$")


def build_back_to_scenarios_handler():
    return CallbackQueryHandler(
        back_to_scenarios, pattern=rf"^{CMD.BACK_TO_SCENARIOS}$"
    )


def build_show_parameters_handler():
    return CallbackQueryHandler(show_parameters, pattern=rf"^{CMD.SHOW_PARAMETERS}$")


def build_back_to_options_handler():
    return CallbackQueryHandler(back_to_options, pattern=rf"^{CMD.BACK_TO_OPTIONS}$")


def build_choose_parameter_handler():
    return CallbackQueryHandler(choose_parameter, pattern=r"^param_\d+$")


def build_back_handler():
    return CallbackQueryHandler(back, pattern=rf"^{CMD.MENU}$")


def build_choose_scenario_handler():
    return CallbackQueryHandler(choose_scenario, pattern=r"^\d*$")


def build_delete_scenario_handler():
    return CallbackQueryHandler(delete_scenario, pattern=rf"^{CMD.DELETE_SCENARIO}$")


def build_fill_scenario_handler():
    return CallbackQueryHandler(fill_scenario, pattern=rf"^{CMD.FILL_SCENARIO}$")


def build_rename_scenario_handler():
    return CallbackQueryHandler(rename_scenario, pattern=rf"^{CMD.RENAME_SCENARIO}$")


def build_get_new_scenario_name_handler():
    return MessageHandler(filters.TEXT, get_new_scenario_name)


def build_confirm_delete_handler():
    return CallbackQueryHandler(confirm_delete, pattern=rf"^{CMD.CONFIRM}$")


def build_cancel_delete_handler():
    return CallbackQueryHandler(cancel_delete, pattern=rf"^{CMD.DENY}$")


def build_add_parameters_handler():
    pattern = f"^({CMD.CONFIRM}|{CMD.DENY})$"
    return CallbackQueryHandler(handle_add_parameters, pattern=pattern)


def build_create_scenario_handler():
    # Entry point and nested state machine for creating a scenario
    param_handler = build_direct_conversation_handler(
        entry_points=[], map_to_parent={END: END}
    )
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(create_scenario, pattern=CMD.CREATE_SCENARIO)
        ],
        states={
            Scenario.NAME: [MessageHandler(filters.TEXT, get_scenario_name)],
            Scenario.ADD_PARAMETERS: [build_add_parameters_handler()],
            Scenario.PARAMETERS: [param_handler],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={
            END: ScenariosList.SCENARIO,
            Scenario.DENY: ScenariosList.SCENARIO,
        },
    )


# Top-level builders for the full conversation handlers


def build_scenarios_handler():
    create_scenario_conv_handler = build_create_scenario_handler()

    fill_records_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(fill_scenario, pattern=rf"^{CMD.FILL_SCENARIO}$")
        ],
        states={
            RecordStates.VALUE: [build_get_value_handler()],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={END: ScenariosList.OPTION},
    )

    return ConversationHandler(
        entry_points=[build_get_my_scenarios_handler()],
        states={
            ScenariosList.SCENARIO: [
                build_choose_scenario_handler(),
                build_back_handler(),
                create_scenario_conv_handler,
            ],
            ScenariosList.OPTION: [
                build_delete_scenario_handler(),
                fill_records_conv,
                build_show_parameters_handler(),
                build_rename_scenario_handler(),
                build_back_to_scenarios_handler(),
            ],
            ScenariosList.DELETE_CONFIRM: [
                build_confirm_delete_handler(),
                build_cancel_delete_handler(),
                build_back_handler(),
            ],
            ScenariosList.RENAME: [
                build_get_new_scenario_name_handler(),
            ],
            ScenariosList.PARAMETERS: [
                build_choose_parameter_handler(),
                build_back_to_options_handler(),
            ],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={END: Menu.CHOOSING_OPTION},
    )


scenarios_handler = build_scenarios_handler()
