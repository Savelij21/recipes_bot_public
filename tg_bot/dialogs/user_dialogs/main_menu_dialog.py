
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

import logging

from lexicon.lexicon import LEXICON
from states.dialogs.user_dialogs_states import StartSG, RecipesSG, SelectionsSG
from external_services import django_api
from dialogs.user_dialogs.errors_dialog import catch_api_error


logger = logging.getLogger(__name__)


# ============================================ MAIN MENU WINDOW ========================================
# Handlers ------------------
async def go_recipes_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(state=RecipesSG.recipes_main_menu)


@catch_api_error
async def go_products_selection_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    selections: list[dict] = await django_api.get_all_products_selections()
    await dialog_manager.start(
        state=SelectionsSG.all_selections,
        data={'selections': selections}
    )

# Getters ------------------

# Window ------------------
main_menu_window = Window(
    Const(LEXICON.main_menu_text),
    Column(
        Button(
            text=Const('Рецепты 🥣'),
            id='recipes',
            on_click=go_recipes_dialog
        ),
        Button(
            text=Const('Подборки продуктов 🛍'),
            id='products_selection',
            on_click=go_products_selection_dialog
        ),
    ),
    state=StartSG.main_menu
)

# =================================== DIALOG =======================================
main_menu_dialog = Dialog(
    main_menu_window,
)
