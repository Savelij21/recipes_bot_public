import asyncio

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import SwitchTo, Start, Column, Button
from aiogram_dialog.widgets.text import Const

from external_services.django_api import Response
from filters.is_admin import IsAdmin
from states.dialogs.admin_dialogs_states import (AdminModeMenuDialogSG,
                                                 AdminModeBroadcastDialogSG,
                                                 AdminModeScheduledJobsDialogSG)
from dialogs.user_dialogs.errors_dialog import catch_api_error
from external_services import django_api


# ==================================== ADMIN MENU WINDOW =======================================================
# Handlers -----------------------------------
@catch_api_error
async def process_db_backup(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    res: Response = await django_api.db_backup()
    if res.status in [200, 201]:
        await callback.message.edit_text(
            text='Бэкап БД успешно создан и сохранен на Yandex Cloud ☑️',
            reply_markup=None
        )
    else:
        await callback.message.edit_text(
            text=f'Ошибка создания резервной копии БД ❌\n\n{res.json}',
            reply_markup=None
        )
    await asyncio.sleep(3)
    await dialog_manager.start(AdminModeMenuDialogSG.start, mode=StartMode.RESET_STACK)

# Getters -----------------------------------

# Window -------------------------------------
admin_menu_window: Window = Window(
    Const('Режим администратора 👨🏻‍💼:'),
    Column(
        Start(
            text=Const('Новая рассылка ✉️'),
            id='newsletter',
            state=AdminModeBroadcastDialogSG.start
        ),
        Start(
            text=Const('Запланированные задачи ⏰'),
            id='scheduled_tasks',
            state=AdminModeScheduledJobsDialogSG.start
        ),
        Button(
            text=Const('Резервная копия БД 🗄'),
            id='db_backup',
            on_click=process_db_backup
        ),
        SwitchTo(
            text=Const('🚪 Выход'),
            id='exit',
            state=AdminModeMenuDialogSG.exit
        )
    ),
    state=AdminModeMenuDialogSG.start
)


# =============================== EXIT ADMIN MENU WINDOW =======================================================
# Handlers -----------------------------------

# Getters -----------------------------------

# Window -------------------------------------
exit_admin_menu_window: Window = Window(
    Const('Выход из режима администратора ❌'),
    state=AdminModeMenuDialogSG.exit
)


# ======================================== DIALOG ========================================================
admin_menu_dialog = Dialog(
    admin_menu_window,
    exit_admin_menu_window
)


# DIALOG FILTERS
admin_menu_dialog.message.filter(IsAdmin())
admin_menu_dialog.callback_query.filter(IsAdmin())
