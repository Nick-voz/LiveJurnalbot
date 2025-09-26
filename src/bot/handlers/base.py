from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END


async def unexpected_err(update: Update, _) -> None:
    await update.message.reply_text("unexpected err")


async def cancel(update: Update, _) -> int:
    await update.message.reply_text("conv canceled")
    return END


async def send_menu(update: Update, _) -> None:
    reply_text = f"Hellow {update.effective_chat.first_name}"

    buttons = [
        [
            InlineKeyboardButton(text="Scenarios", callback_data=CMD.SCENARIOS_LIST),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if update.message is not None:
        await update.message.reply_text(reply_text, reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(reply_text, reply_markup=keyboard)


# Builders for handlers (optional, keeps pattern consistent with other modules)


def build_unexpected_err_handler() -> MessageHandler:
    return MessageHandler(filters.ALL, unexpected_err)


def build_cancel_handler() -> CommandHandler:
    return CommandHandler(CMD.CANCEL, cancel)


# Public exports / registration

unexpected_err_handler = build_unexpected_err_handler()
cancel_handler = build_cancel_handler()
