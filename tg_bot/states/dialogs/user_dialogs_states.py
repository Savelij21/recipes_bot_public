from aiogram.fsm.state import State, StatesGroup


# MAIN MENU
class StartSG(StatesGroup):
    main_menu = State()


# RECIPES
class RecipesSG(StatesGroup):
    recipes_main_menu = State()

    all_recipes = State()

    categories = State()
    category_recipes = State()

    ingredients = State()
    ingredient_recipes = State()

    calories_ranges = State()
    calories_range_recipes = State()

    random_recipe = State()


# SELECTIONS
class SelectionsSG(StatesGroup):
    all_selections = State()
    selection_detail = State()


# ERRORS
class ErrorsSG(StatesGroup):
    api_error = State()
