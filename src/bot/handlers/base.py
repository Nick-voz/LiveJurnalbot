from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.keyboards.scenarios import get_keyboard_scenario_options
from src.bot.keyboards.scenarios import get_keyboard_scenarios
from src.db.repository import get_user_scenario_by_id
from src.db.repository import get_user_scenarios_by_chat


async def unexpected_err(update: Update, _) -> None:
    await update.message.reply_text("unexpected err")


async def cancel(update: Update, _) -> int:
    await update.message.reply_text("conv canceled")
    return END


async def send_menu(update: Update, _) -> None:
    buttons = [
        [
            InlineKeyboardButton(text="Scenarios", callback_data=CMD.SCENARIOS_LIST),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    reply_text = "Choose an option:"

    if update.message is not None:
        await update.message.reply_text(reply_text, reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(reply_text, reply_markup=keyboard)


def prepare_scenarios_list(chat_id):
    scenarios = get_user_scenarios_by_chat(chat_id)
    reply_text = "Choose scenario to interact or tap back to menu."
    reply_markup = get_keyboard_scenarios(scenarios)
    return reply_text, reply_markup


def build_unexpected_err_handler() -> MessageHandler:
    return MessageHandler(filters.ALL, unexpected_err)


def build_cancel_handler() -> CommandHandler:
    return CommandHandler(CMD.CANCEL, cancel)


async def start_scenario_selection(
    update: Update,
    _,
    return_state: int,
    message: str = "Select scenario",
) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)
    reply_markup = get_keyboard_scenarios(user_scenarios)
    await update.message.reply_text(message, reply_markup=reply_markup)
    return return_state


async def display_scenario_options(
    update: Update,
    _,
    scenario_id: int,
) -> None:
    scenario = get_user_scenario_by_id(scenario_id)
    reply_text = f"Chose option for scenario: {scenario.scenario.name}"
    reply_markup = get_keyboard_scenario_options()
    await update.callback_query.edit_message_text(reply_text, reply_markup=reply_markup)
