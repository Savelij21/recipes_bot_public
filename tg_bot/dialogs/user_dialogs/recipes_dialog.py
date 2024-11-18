import asyncio

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.kbd import Button, Column, SwitchTo, Select, ListGroup, Url, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from lexicon.lexicon import LEXICON
from states.dialogs.user_dialogs_states import RecipesSG, StartSG
from external_services import django_api
from dialogs.user_dialogs.errors_dialog import catch_api_error

import logging


logger = logging.getLogger(__name__)


# ====================================== RECIPES MAIN MENU ======================================
# Handlers ----------------------------
@catch_api_error
async def switch_to_all_recipes(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    all_recipes: list[dict] = await django_api.get_all_recipes()
    dialog_manager.dialog_data.update({'all_recipes': all_recipes})
    await dialog_manager.switch_to(RecipesSG.all_recipes)


# -- switch to section
@catch_api_error
async def switch_to_categories(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    categories: list[dict] = await django_api.get_all_categories()
    dialog_manager.dialog_data.update({'categories': categories})
    await dialog_manager.switch_to(RecipesSG.categories)


@catch_api_error
async def switch_to_ingredients(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    ingredients: list[dict] = await django_api.get_all_ingredients()
    dialog_manager.dialog_data.update({'ingredients': ingredients})
    await dialog_manager.switch_to(RecipesSG.ingredients)


@catch_api_error
async def switch_to_calories_ranges(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    calories_ranges: list[dict] = await django_api.get_calories_ranges()
    dialog_manager.dialog_data.update({'calories_ranges': calories_ranges})
    await dialog_manager.switch_to(RecipesSG.calories_ranges)


@catch_api_error
async def switch_to_random_recipe(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    random_recipe: dict = await django_api.get_random_recipe()
    dialog_manager.dialog_data.update({'random_recipe': random_recipe})

    await callback.message.edit_text('Не знаешь чем таким вкусным \nи полезным себя побаловать? 😋')
    await asyncio.sleep(2.5)
    await callback.message.edit_text('Сейчас подготовим для тебя кое-что интересное ✨')
    await asyncio.sleep(2.5)
    await callback.message.edit_text('Подбираем лучшие ингредиенты 🥣')
    await asyncio.sleep(2.5)
    await callback.message.edit_text('Нам кажется, что сегодня лучший вариант для тебя это...')
    await asyncio.sleep(2.5)

    await dialog_manager.switch_to(RecipesSG.random_recipe)


async def switch_to_main_menu(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.main_menu, mode=StartMode.RESET_STACK)


# Getters ------------------------------

# Window -----------------------------
recipes_main_menu_window: Window = Window(
    Const(LEXICON.recipes_main_menu_text),
    Column(
        Button(
            text=Const('Все рецепты'),
            id='all_recipes',
            on_click=switch_to_all_recipes
        ),
        Button(
            text=Const('По категориям 🗂'),
            id='by_categories',
            on_click=switch_to_categories
        ),
        Button(
            text=Const('По продуктам 🥦'),
            id='by_ingredients',
            on_click=switch_to_ingredients
        ),
        Button(
            text=Const('По калориям ⚖️'),
            id='by_calories',
            on_click=switch_to_calories_ranges
        ),
        Button(
            text=Const('Случайный рецепт 🪄'),
            id='random_recipe',
            on_click=switch_to_random_recipe
        ),
        Button(
            text=Const('⬅️ В главное меню'),
            id='back_to_main_menu',
            on_click=switch_to_main_menu
        ),
    ),
    state=RecipesSG.recipes_main_menu
)


# ========================================== ALL RECIPES WINDOW ==========================================
# Handlers --------------------------

# Getters ----------------------------
async def all_recipes_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    recipes: list[dict] = dialog_manager.dialog_data.get('all_recipes')
    return {
        'recipes': recipes,
        'recipes_count': len(recipes),
    }

# Window -----------------------------
all_recipes_window: Window = Window(
    Format('<b>Все рецепты [{recipes_count}]</b>'),
    ScrollingGroup(
        ListGroup(
            Url(
                text=Format('{item[title]}'),
                url=Format('{item[chanel_url]}'),
            ),
            id='recipes_list',
            items='recipes',
            item_id_getter=lambda item: item['id'],
        ),
        id='all_recipes_scrolling_group',
        width=1,
        height=10,
        hide_on_single_page=True
    ),
    SwitchTo(
        text=Const('⬅️ В меню рецептов'),
        id='back_to_recipes_main_menu',
        state=RecipesSG.recipes_main_menu
    ),
    getter=all_recipes_getter,
    state=RecipesSG.all_recipes
)


# ======================================= CATEGORIES ===============================================
# ==================================== ALL CATEGORIES WINDOW =======================================

# Handlers --------------------
@catch_api_error
async def select_category(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    category: dict = await django_api.get_category(int(item_id))
    recipes: list[dict] = await django_api.get_category_recipes(int(item_id))
    dialog_manager.dialog_data.update({
        'recipes': recipes,
        'category': category
    })
    await dialog_manager.switch_to(RecipesSG.category_recipes)


# Getters ---------------------
async def categories_list_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    categories: list[dict] = dialog_manager.dialog_data.get('categories')
    return {
        'categories': categories,
        'categories_count': len(categories),
    }


# Window ---------------------
all_categories_window: Window = Window(
    Format('<b>Список категорий</b> 🗂 <b>[{categories_count}]</b>'),
    ScrollingGroup(
        Select(
            text=Format('{item[beauty_title]} [{item[recipes_count]}]'),
            id='categories_list',
            items='categories',
            item_id_getter=lambda item: item['id'],
            on_click=select_category,
        ),
        id='categories_scrolling_group',
        width=1,
        height=10,
        hide_on_single_page=True
    ),
    SwitchTo(
        text=Const('⬅️ В меню рецептов'),
        id='back_to_recipes_main_menu',
        state=RecipesSG.recipes_main_menu
    ),
    getter=categories_list_getter,
    state=RecipesSG.categories
)

# =================================== RECIPES OF CATEGORY ===========================================

# Handlers -------------------------


# Getters --------------------------
async def category_recipes_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    category: dict = dialog_manager.dialog_data.get('category')
    recipes: list[dict] = dialog_manager.dialog_data.get('recipes')
    return {
        'recipes': recipes,
        'category': category
    }


# Window ---------------------------
category_recipes_window: Window = Window(
    Format('Рецепты категории: <b>{category[beauty_title]}</b>'),
    ScrollingGroup(
        ListGroup(
            Url(
                text=Format('{item[title]}'),
                url=Format('{item[chanel_url]}'),
            ),
            id='recipes_list',
            items='recipes',
            item_id_getter=lambda item: item['id'],
        ),
        id='recipes_scrolling_group',
        width=1,
        height=10,
        hide_on_single_page=True
    ),
    SwitchTo(
        text=Const('⬅️ К категориям'),
        id='back_to_categories',
        state=RecipesSG.categories
    ),
    getter=category_recipes_getter,
    state=RecipesSG.category_recipes
)


# ======================================= INGREDIENTS ===========================================
# =================================== ALL INGREDIENTS WINDOW ===========================================

# Handlers ---------------------
@catch_api_error
async def select_ingredient(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    ingredient: dict = await django_api.get_ingredient(int(item_id))
    recipes: list[dict] = await django_api.get_ingredient_recipes(int(item_id))
    dialog_manager.dialog_data.update({
        'recipes': recipes,
        'ingredient': ingredient
    })
    await dialog_manager.switch_to(RecipesSG.ingredient_recipes)


# Getters ----------------------
async def ingredients_list_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    ingredients: list[dict] = dialog_manager.dialog_data.get('ingredients')
    return {
        'ingredients': ingredients,
        'ingredients_count': len(ingredients),
    }


# Window -----------------------
all_ingredients_window: Window = Window(
    Format('<b>Список продуктов</b> 🥦 <b>[{ingredients_count}]</b>'),
    ScrollingGroup(
        Select(
            text=Format('{item[name]} [{item[recipes_count]}]'),
            id='ingredients_list',
            items='ingredients',
            item_id_getter=lambda item: item['id'],
            on_click=select_ingredient,
        ),
        id='ingredients_scrolling_group',
        width=1,
        height=10,
        hide_on_single_page=True
    ),
    SwitchTo(
        text=Const('⬅️ В меню рецептов'),
        id='back_to_recipes_main_menu',
        state=RecipesSG.recipes_main_menu
    ),
    getter=ingredients_list_getter,
    state=RecipesSG.ingredients
)


# ================================== RECIPES OF INGREDIENT ===========================================

# Handlers -----------------------

# Getters --------------------------
async def ingredient_recipes_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    ingredient: dict = dialog_manager.dialog_data.get('ingredient')
    recipes: list[dict] = dialog_manager.dialog_data.get('recipes')
    return {
        'recipes': recipes,
        'ingredient': ingredient
    }


# Window ---------------------------
ingredient_recipes_window: Window = Window(
        Format('Рецепты с продуктом: <b>{ingredient[name]}</b>'),
        ScrollingGroup(
            ListGroup(
                Url(
                    text=Format('{item[title]}'),
                    url=Format('{item[chanel_url]}'),
                ),
                id='recipes_list',
                items='recipes',
                item_id_getter=lambda item: item['id'],
            ),
            id='recipes_scrolling_group',
            width=1,
            height=10,
            hide_on_single_page=True
        ),
        SwitchTo(
            text=Const('⬅️ К продуктам'),
            id='back_to_ingredients',
            state=RecipesSG.ingredients
        ),
        getter=ingredient_recipes_getter,
        state=RecipesSG.ingredient_recipes
    )


# ======================================= CALORIES RANGES ===========================================
# =================================== CALORIES RANGES LIST WINDOW ===========================================

# Handlers ---------------------
@catch_api_error
async def select_calories_range(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    calories_range = await django_api.get_calories_range(int(item_id))
    recipes: list[dict] = await django_api.get_calories_range_recipes(int(item_id))
    dialog_manager.dialog_data.update({
        'recipes': recipes,
        'calories_range': calories_range
    })
    await dialog_manager.switch_to(RecipesSG.calories_range_recipes)


# Getters -------------------
async def calories_ranges_list_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    calories_ranges: list[dict] = dialog_manager.dialog_data.get('calories_ranges')
    return {
        'calories_ranges': calories_ranges,
        'calories_ranges_count': len(calories_ranges),
    }


# Window ---------------------
all_calories_ranges_window: Window = Window(
    Format('<b>Калоражи на <u>100</u> грамм</b> ⚖️ <b>[{calories_ranges_count}]</b>'),
    ScrollingGroup(
        Select(
            text=Format('{item[min]} <--> {item[max]} [{item[recipes_count]}]'),
            id='calories_ranges_list',
            items='calories_ranges',
            item_id_getter=lambda item: item['id'],
            on_click=select_calories_range,
        ),
        id='calories_ranges_scrolling_group',
        width=1,
        height=10,
        hide_on_single_page=True
    ),
    SwitchTo(
        text=Const('⬅️ В меню рецептов'),
        id='back_to_recipes_main_menu',
        state=RecipesSG.recipes_main_menu
    ),
    getter=calories_ranges_list_getter,
    state=RecipesSG.calories_ranges
)


# ======================================= CALORIES RANGE RECIPES WINDOW =========================================

# Handlers ---------------------

# Getters -----------------------------
async def calories_range_recipes_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    calories_range: dict = dialog_manager.dialog_data.get('calories_range')
    recipes: list[dict] = dialog_manager.dialog_data.get('recipes')
    return {
        'recipes': recipes,
        'calories_range': calories_range
    }


# Window -----------------------------
calories_range_recipes: Window = Window(
    Format('Рецепты диапазона: <b>{calories_range[min]} &lt--&gt {calories_range[max]} килокалорий</b>'),
    ScrollingGroup(
        ListGroup(
            Url(
                text=Format('{item[title]}'),
                url=Format('{item[chanel_url]}'),
            ),
            id='recipes_list',
            items='recipes',
            item_id_getter=lambda item: item['id'],
        ),
        id='recipes_scrolling_group',
        width=1,
        height=10,
        hide_on_single_page=True
    ),
    SwitchTo(
        text=Const('⬅️ К продуктам'),
        id='back_to_ingredients',
        state=RecipesSG.calories_ranges
    ),
    getter=calories_range_recipes_getter,
    state=RecipesSG.calories_range_recipes
)


# ======================================== RANDOM RECIPE WINDOW =========================================

# Handlers ----------------------

# Getters ----------------------
async def random_recipe_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    random_recipe: dict = dialog_manager.dialog_data.get('random_recipe')
    return {
        'random_recipe': random_recipe
    }

# Window -----------------------
random_recipe_window: Window = Window(
    Const('Нам кажется, что сегодня лучший вариант для тебя это...\n'),
    Format('<b>!!! <u>{random_recipe[title]}</u> !!!</b>\n'),
    Const('Жми на кнопку, читай описание и беги скорее готовить эту вкусноту! 👨‍🍳'),
    Url(
        text=Format('Ссылка на рецепт ↗️'),
        url=Format('{random_recipe[chanel_url]}'),
    ),
    SwitchTo(
        text=Const('⬅️ В меню рецептов'),
        id='back_to_recipes_main_menu',
        state=RecipesSG.recipes_main_menu
    ),
    getter=random_recipe_getter,
    state=RecipesSG.random_recipe
)


# ========================================== DIALOG ==========================================
recipes_dialog = Dialog(
    recipes_main_menu_window,

    all_recipes_window,

    all_categories_window,
    category_recipes_window,

    all_ingredients_window,
    ingredient_recipes_window,

    all_calories_ranges_window,
    calories_range_recipes,

    random_recipe_window,
)
