import csv
import io
from collections import defaultdict
from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

from src.bot.constants.commands_text import CMD
from src.bot.constants.conversation_states import END
from src.bot.constants.conversation_states import ExportScenario
from src.bot.constants.user_data_keys import UDK
from src.bot.handlers.base import build_cancel_handler
from src.bot.handlers.base import build_unexpected_err_handler
from src.bot.handlers.base import display_scenario_options
from src.bot.keyboards.scenarios import get_keyboard_export_file_types
from src.db.models import Value
from src.db.repository import get_scenario_values
from src.db.repository import get_user_scenario_by_id


def values_to_csv(values: list[Value]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    grouped = defaultdict(dict)
    param_names = set()
    for value in values:
        dt_str = value.record.created_at.isoformat()
        param_names.add(value.parameter.name)
        grouped[dt_str][value.parameter.name] = value.value
    sorted_params = sorted(param_names)
    headers = sorted_params + ["DateTime"]
    writer.writerow(headers)
    for dt_str in sorted(grouped.keys()):
        row = [grouped[dt_str].get(param, "") for param in sorted_params] + [dt_str]
        writer.writerow(row)

    csv_content = output.getvalue()
    output.close()
    return csv_content


async def prepare_export_file(
    user_scenario_id: int, file_type: str
) -> io.BytesIO:
    if file_type != "csv":
        raise ValueError(f"Unsupported file type: {file_type}")

    values = get_scenario_values(user_scenario_id)
    csv_content = values_to_csv(values)
    file = io.BytesIO(csv_content.encode("utf-8"))
    file.seek(0)
    return file


async def export_scenario(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    keyboard = get_keyboard_export_file_types()
    await update.callback_query.edit_message_text(
        "Select file type:", reply_markup=keyboard
    )
    return ExportScenario.FILE_TYPE


async def get_file_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_scenario_id = context.user_data[UDK.USER_SCENARIO_ID]
    scenario = get_user_scenario_by_id(user_scenario_id)
    file_type = update.callback_query.data
    file = await prepare_export_file(user_scenario_id, file_type)
    await update.effective_chat.send_document(
        file, filename=f"scenario_{scenario.scenario.name}.{file_type}"
    )
    await display_scenario_options(update, context, user_scenario_id)
    return END


# Builders for handlers
def build_export_scenario_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(export_scenario, pattern=rf"^{CMD.EXPORT_SCENARIO}$")
        ],
        states={
            ExportScenario.FILE_TYPE: [CallbackQueryHandler(get_file_type)],
        },
        fallbacks=[build_cancel_handler(), build_unexpected_err_handler()],
        map_to_parent={END: END},
    )
