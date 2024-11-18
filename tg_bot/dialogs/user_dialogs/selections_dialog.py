
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Select, Url, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

import logging

from lexicon.lexicon import LEXICON
from states.dialogs.user_dialogs_states import SelectionsSG, StartSG
from external_services import django_api
from dialogs.user_dialogs.errors_dialog import catch_api_error


logger = logging.getLogger(__name__)


# ========================================== SELECTIONS LIST WINDOW ========================================
# Handlers ----------------------------
async def switch_to_main_menu(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.main_menu, mode=StartMode.RESET_STACK)


@catch_api_error
async def select_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    selection: dict = await django_api.get_products_selection(int(item_id))
    dialog_manager.dialog_data.update({'selection': selection})
    await dialog_manager.switch_to(SelectionsSG.selection_detail)


# Getters -----------------------------
async def all_selections_getter(dialog_manager: DialogManager, **kwargs):
    return {'selections': dialog_manager.start_data.get('selections')}

# Window ------------------------------
all_selections_window = Window(
    Const(LEXICON.all_selections_text),
    ScrollingGroup(
        Select(
            text=Format('{item[beauty_title]}'),
            id='selections_list',
            items='selections',
            item_id_getter=lambda item: item['id'],
            on_click=select_selection,
        ),
        id='selections_scrolling_group',
        width=1,
        height=10,
        hide_on_single_page=True
    ),
    Button(
        text=Const('⬅️ В главное меню'),
        id='back_to_main_menu',
        on_click=switch_to_main_menu
    ),
    getter=all_selections_getter,
    state=SelectionsSG.all_selections
)


# ======================================== SELECTION DETAIL WINDOW ========================================
# Handlers ----------------------------

# Getters -----------------------------
async def detail_selection_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    return {'selection': dialog_manager.dialog_data.get('selection')}

# Window ------------------------------
selection_detail_window = Window(
    Format('Подборка: <b>{selection[beauty_title]}</b>\n'),
    Format('<a href="{selection[video_url]}">Смотреть видео 👇</a>'),
    Url(text=Format('YouTube 🎥'), url=Format('{selection[video_url]}')),
    SwitchTo(
        id='back_to_all_selections',
        text=Const('⬅️ К подборкам'),
        state=SelectionsSG.all_selections
    ),
    getter=detail_selection_getter,
    state=SelectionsSG.selection_detail
)


# ================================ DIALOG ================================
selections_dialog = Dialog(
    all_selections_window,
    selection_detail_window
)
