
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_back_to_admin_menu_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text='⬅️ В админ меню',
            callback_data='admin'
        )
    )
    return kb_builder.as_markup()


# Broadcast process ----------------------------------------------
def get_broadcast_process_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text='Остановить ⭕️',
            callback_data='stop_broadcast'
        ),
        width=1
    )
    return kb_builder.as_markup()


def get_confirm_stop_broadcast_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text='Остановить ⭕️',
            callback_data='confirm_stop_broadcast'
        ),
        InlineKeyboardButton(
            text='Продолжить рассылку 🟢',
            callback_data='cancel_stop_broadcast'
        ),
        width=1
    )
    return kb_builder.as_markup()
