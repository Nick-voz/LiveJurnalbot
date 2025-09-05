from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.conversation_states import ReminderStrategyStates
from src.bot.hendlers.base import unexpected_err_handler
from src.db.models import ReminderStrategy
from src.db.repository import find_or_create_reminder_strategy
from src.db.repository import find_user_scenario_by_name
from src.db.repository import get_user_scenarios_by_chat

REMINDER_STRATEGY_KEY = 1
END = -1


async def start_reminder_strategy_conv(update: Update, _) -> int:
    user_scenarios = get_user_scenarios_by_chat(chat_id=update.effective_chat.id)
    replay_text = f"choose users scenario {[e.scenario.name for e in user_scenarios]}"
    await update.message.reply_text(replay_text)
    return ReminderStrategyStates.USER_SCENARIO


async def choose_user_scenario(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = update.message.text
    chat_id = update.effective_chat.id
    user_scenio = find_user_scenario_by_name(name, chat_id)

    if user_scenio is None:
        await update.message.reply_text("try again")
        return ReminderStrategyStates.USER_SCENARIO

    strategy = find_or_create_reminder_strategy(user_scenio)
    context.user_data[REMINDER_STRATEGY_KEY] = strategy

    await update.message.reply_text(f"sent module")

    return ReminderStrategyStates.MODULE


async def get_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    strategy: ReminderStrategy = context.user_data.get(REMINDER_STRATEGY_KEY)

    if strategy is None:
        await update.message.reply_text("something want wrong")
        return END

    try:
        strategy.module = int(update.message.text)
    except ValueError:
        return ReminderStrategyStates.MODULE

    await update.message.reply_text(f"send shift")

    return ReminderStrategyStates.SHIFT


async def get_shift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    strategy: ReminderStrategy = context.user_data.get(REMINDER_STRATEGY_KEY)
    if strategy is None:
        await update.message.reply_text("something want wrong")
        return END

    try:
        strategy.shift = int(update.message.text)
    except ValueError:
        return ReminderStrategyStates.SHIFT

    strategy.save()
    await update.message.reply_text(f"success")

    return END


start_strategy_conv_hendler = CommandHandler(
    "set_strateg", start_reminder_strategy_conv
)
choose_user_scenario_hendler = MessageHandler(filters.TEXT, choose_user_scenario)
get_module_hendler = MessageHandler(filters.TEXT, get_module)
get_shift_hendler = MessageHandler(filters.TEXT, get_shift)


def register(app: Application):
    app.add_handler(
        ConversationHandler(
            entry_points=(start_strategy_conv_hendler,),
            states={
                ReminderStrategyStates.USER_SCENARIO: (choose_user_scenario_hendler,),
                ReminderStrategyStates.MODULE: (get_module_hendler,),
                ReminderStrategyStates.SHIFT: (get_shift_hendler,),
            },
            fallbacks=(unexpected_err_handler,),
        )
    )
