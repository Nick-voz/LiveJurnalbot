from os import umask

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


async def send_menu(update: Update, _):
    reply_text = f"Hellow {update.effective_chat.first_name}"

    buttons = [
        [
            InlineKeyboardButton(
                text="Add scenario", callback_data=CMD.CREATE_SCENARIO
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if update.message is not None:
        await update.message.reply_text(reply_text, reply_markup=keyboard)
    else:
        await update.inline_query.message(reply_text, reply_markup=keyboard)


unexpected_err_handler = MessageHandler(filters.ALL, unexpected_err)
cancel_handler = CommandHandler(CMD.CANCEL, cancel)
