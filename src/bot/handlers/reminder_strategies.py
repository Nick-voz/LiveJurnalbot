from telegram import Update
from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import ReminderStrategyStates
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import cancel_handler
from src.bot.handlers.base import unexpected_err_handler
from src.bot.utils import generate_inline_keyboard_user_scenarios
from src.db.models import ReminderStrategy
from src.db.repository import find_or_create_reminder_strategy
from src.db.repository import find_user_scenario_by_name
from src.db.repository import get_user_scenarios_by_chat


async def start_reminder_strategy_conv(update: Update, _) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)
    reply_markup = generate_inline_keyboard_user_scenarios(user_scenarios)
    await update.message.reply_text("Select scenario", reply_markup=reply_markup)
    return ReminderStrategyStates.USER_SCENARIO


async def choose_user_scenario(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    name = query.data
    chat_id = update.effective_chat.id
    user_scenio = find_user_scenario_by_name(name, chat_id)

    if user_scenio is None:
        await query.message.reply_text("try again")
        return ReminderStrategyStates.USER_SCENARIO

    strategy = find_or_create_reminder_strategy(user_scenio)
    context.user_data[UDK.REMINDER_STRATEGY] = strategy

    await query.message.reply_text("sent module")

    return ReminderStrategyStates.MODULE


async def get_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    strategy: ReminderStrategy = context.user_data.get(UDK.REMINDER_STRATEGY)

    if strategy is None:
        await update.message.reply_text("something want wrong")
        return END

    try:
        strategy.module = int(update.message.text)
    except ValueError:
        return ReminderStrategyStates.MODULE

    await update.message.reply_text("send shift")

    return ReminderStrategyStates.SHIFT


async def get_shift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    strategy: ReminderStrategy = context.user_data.get(UDK.REMINDER_STRATEGY)
    if strategy is None:
        await update.message.reply_text("something want wrong")
        return END

    try:
        strategy.shift = int(update.message.text)
    except ValueError:
        return ReminderStrategyStates.SHIFT

    strategy.save()
    await update.message.reply_text("success")

    return END


start_strategy_conv_handler = CommandHandler(
    CMD.CREATE_STRATEGY, start_reminder_strategy_conv
)
choose_user_scenario_handler = CallbackQueryHandler(choose_user_scenario)
get_module_handler = MessageHandler(filters.TEXT, get_module)
get_shift_handler = MessageHandler(filters.TEXT, get_shift)


def register(app: Application):
    app.add_handler(
        ConversationHandler(
            entry_points=(start_strategy_conv_handler,),
            states={
                ReminderStrategyStates.USER_SCENARIO: (choose_user_scenario_handler,),
                ReminderStrategyStates.MODULE: (get_module_handler,),
                ReminderStrategyStates.SHIFT: (get_shift_handler,),
            },
            fallbacks=(cancel_handler, unexpected_err_handler),
        )
    )
