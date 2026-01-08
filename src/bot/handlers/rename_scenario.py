from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import ScenariosList
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.scenarios_list import send_scenarios_list
from src.db.repository import update_user_scenario_name


async def rename_scenario(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Send the new name for the scenario.")
    return ScenariosList.RENAME


async def get_new_scenario_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_name = update.message.text
    user_scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    update_user_scenario_name(user_scenario_id, new_name)
    await update.message.reply_text(f"Scenario renamed to '{new_name}'.")
    await send_scenarios_list(update)
    return END


# Builders for handlers
def build_rename_scenario_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(rename_scenario, pattern=rf"^{CMD.RENAME_SCENARIO}$")
        ],
        states={
            ScenariosList.RENAME: [MessageHandler(filters.TEXT, get_new_scenario_name)],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={END: END},
    )
