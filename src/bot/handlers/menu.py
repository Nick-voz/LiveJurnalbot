from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler

from src.bot.constants.commands_text import CMD
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.base import send_menu
from src.bot.handlers.create_scenario import build_create_scenario_handler
from src.bot.handlers.delete_scenario import build_delete_scenario_handler
from src.bot.handlers.fill_scenario import build_fill_scenario_handler
from src.bot.handlers.rename_scenario import build_rename_scenario_handler
from src.bot.handlers.scenario_options import build_back_to_options_handler
from src.bot.handlers.scenario_options import build_back_to_scenarios_handler
from src.bot.handlers.scenario_options import build_choose_scenario_handler
from src.bot.handlers.scenario_parameters import build_choose_parameter_handler
from src.bot.handlers.scenario_parameters import build_show_parameters_handler
from src.bot.handlers.scenarios_list import build_get_my_scenarios_handler
from src.db.repository import create_user
from src.db.repository import get_user_by_chat


async def start(update: Update, _) -> None:
    remember_user_if_not_yet(update.effective_chat.id)
    reply_text = (
        f"Hello {update.effective_chat.first_name}!\n\n"
        "Welcome to LiveJurnalbot, your personal journaling assistant.\n"
        "Track your daily parameters in custom scenarios (e.g., health, habits).\n\n"
        "Use /menu to start managing your scenarios."
    )
    await update.message.reply_text(reply_text)


def remember_user_if_not_yet(chat_id: int) -> None:
    user = get_user_by_chat(chat_id)
    if user is None:
        create_user(chat_id)
        user = get_user_by_chat(chat_id)


async def menu(update: Update, _) -> None:
    remember_user_if_not_yet(update.effective_chat.id)
    await send_menu(update, _)


# Builder: create the menu command handler
def build_menu_command_handler():
    return CommandHandler(CMD.MENU, menu)


def register(app: Application):
    app.add_handler(CommandHandler(CMD.START, start))
    app.add_handler(build_menu_command_handler())
    app.add_handler(build_get_my_scenarios_handler())
    app.add_handler(build_choose_scenario_handler())
    app.add_handler(build_back_to_scenarios_handler())
    app.add_handler(build_show_parameters_handler())
    app.add_handler(build_back_to_options_handler())
    app.add_handler(build_choose_parameter_handler())
    app.add_handler(build_fill_scenario_handler())
    app.add_handler(build_delete_scenario_handler())
    app.add_handler(build_rename_scenario_handler())
    app.add_handler(build_create_scenario_handler())
    app.add_handler(build_cancel_handler())
    app.add_handler(build_unexpected_err_handler())
