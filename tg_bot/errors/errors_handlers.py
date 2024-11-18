
from aiogram import Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import Update, ErrorEvent
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.api.exceptions import DialogsError

import logging

from states.dialogs.user_dialogs_states import StartSG

logger = logging.getLogger(__name__)

router = Router()


@router.error(ExceptionTypeFilter(Exception))
async def error_handler(event: ErrorEvent, *args, **kwargs):
    exception: Exception = event.exception
    update: Update = event.update
    # log_str: str = ''

    if isinstance(exception, DialogsError):
        dialog_manager: DialogManager = kwargs.get('dialog_manager')
        await dialog_manager.reset_stack()
        await dialog_manager.start(StartSG.main_menu, mode=StartMode.RESET_STACK)
        log_str = f'[DialogsError] - {event.exception} - RESET DIALOGS STACK'

    else:  # Exception
        log_str = f'[GlobalException] - {event.exception}'

    # finish
    logger.error(log_str, exc_info=True)
    return True











