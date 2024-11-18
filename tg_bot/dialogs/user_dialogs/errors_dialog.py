
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiohttp import ClientError

import logging

from lexicon.lexicon import LEXICON
from states.dialogs.user_dialogs_states import ErrorsSG, StartSG


logger = logging.getLogger(__name__)


# ====================================== API ERROR WINDOW =========================================
# Handlers ----------------------------
async def get_back_to_main_menu(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await dialog_manager.start(StartSG.main_menu, mode=StartMode.RESET_STACK)


# Getters -----------------------------
async def error_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    error_text: str = dialog_manager.start_data.get('error_text', '')
    return {'error_text': error_text}


# Window -------------------------------
api_error_window = Window(
    Const(LEXICON.api_error_text),
    Format('\n\n{error_text}'),
    Button(
        text=Const('⬅️ В главное меню'),
        id='back_to_main_menu',
        on_click=get_back_to_main_menu
    ),
    getter=error_getter,
    state=ErrorsSG.api_error
)

# =========================== DIALOG ===================================
errors_dialog = Dialog(
    api_error_window
)


# Extra Functions -------------------------------
def catch_api_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ClientError as e:
            logger.error(e)
            dialog_manager: DialogManager = args[2]
            await dialog_manager.start(
                state=ErrorsSG.api_error,
                mode=StartMode.RESET_STACK,
                data={'error_text': str(e)}
            )
            return
    return wrapper

