from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import Scenario
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.base import prepare_scenarios_list
from src.bot.handlers.parametrs import build_direct_conversation_handler
from src.bot.keyboards.parametrs import get_continue_keyboard
from src.db.repository import create_user_scenario


async def create_scenario(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    reply_text = "Into next message send the scenario name."
    await update.callback_query.edit_message_text(reply_text)
    return Scenario.NAME


async def get_scenario_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    name = update.message.text
    user_scenario = create_user_scenario(chat_id=chat_id, name=name)
    context.user_data[UDK.USER_SCENARIO_ID] = user_scenario.id
    await update.message.reply_text(
        f"scenario with name: '{name}' was added to your scenarios"
    )
    await update.message.reply_text(
        "Do you want to add parameters to this scenario?",
        reply_markup=get_continue_keyboard(),
    )
    return Scenario.ADD_PARAMETERS


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
        return END
    await query.edit_message_text("Invalid choice. Please try again.")
    return Scenario.ADD_PARAMETERS


# Builder for handler
def build_create_scenario_handler():
    param_handler = build_direct_conversation_handler(
        entry_points=[], map_to_parent={END: END}
    )
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(create_scenario, pattern=CMD.CREATE_SCENARIO)
        ],
        states={
            Scenario.NAME: [MessageHandler(filters.TEXT, get_scenario_name)],
            Scenario.ADD_PARAMETERS: [
                CallbackQueryHandler(
                    handle_add_parameters, pattern=f"^({CMD.CONFIRM}|{CMD.DENY})$"
                )
            ],
            Scenario.PARAMETERS: [param_handler],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={
            END: END,
        },
    )
