from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import Scenario
from src.bot.hendlers.base import cancel_hendler
from src.bot.hendlers.base import unexpected_err_handler
from src.db.repository import create_user_scenario
from src.db.repository import get_user_scenarios_by_chat
from src.templates.env import env


async def get_my_scenarios(update: Update, _) -> None:
    chat_id = update.effective_chat.id
    scenarios = get_user_scenarios_by_chat(chat_id)
    reply_text = env.get_template("scenarios_list.txt").render(scenarios=scenarios)
    await update.message.reply_text(reply_text)


async def create_scenario_cmd(update: Update, _) -> int:
    reply_text = env.get_template("ask_scenario_name.txt").render()
    await update.message.reply_text(reply_text)
    return Scenario.NAME


async def get_scenario_name(update: Update, _) -> int:
    chat_id = update.effective_chat.id
    name = update.message.text
    create_user_scenario(chat_id=chat_id, name=name)
    await update.message.reply_text(
        f"scenario with name: '{name}' was added to your scenarios"
    )
    return END


get_my_scenario_cmd_handler = CommandHandler(CMD.SCENARIOS_LIST, get_my_scenarios)
create_scenario_handler = CommandHandler(CMD.CREATE_SCENARIO, create_scenario_cmd)
get_scenario_name_handler = MessageHandler(filters.TEXT, get_scenario_name)


def register(app: Application):
    app.add_handlers(
        (
            get_my_scenario_cmd_handler,
            ConversationHandler(
                entry_points=(create_scenario_handler,),
                states={
                    Scenario.NAME: (get_scenario_name_handler,),
                },
                fallbacks=(cancel_hendler, unexpected_err_handler),
            ),
        )
    )
