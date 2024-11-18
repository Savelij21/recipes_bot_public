
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, User, ChatMemberUpdated
from aiogram.filters import Command, CommandStart, ChatMemberUpdatedFilter, KICKED
from aiogram_dialog import DialogManager, StartMode

import logging

from dialogs.user_dialogs.errors_dialog import catch_api_error
from states.dialogs.user_dialogs_states import StartSG, ErrorsSG, RecipesSG, SelectionsSG
from external_services import django_api

logger = logging.getLogger(__name__)

router = Router()


# /start ----------------------------------------------------------------------------------------------------------
@router.message(CommandStart())
async def process_start_command(message: Message, dialog_manager: DialogManager):
    await message.chat.do('typing')
    # check if user already exists
    user: User = message.from_user
    try:
        res = await django_api.create_user({
                'tg_id': user.id,
                'username': user.username,
                'name': user.full_name,
                'first_name': user.first_name,
                'last_name': user.last_name
        })

        if res.status == 201:
            logger.info(f'Пользователь {message.from_user.id}#{message.from_user.username} добавлен в БД')
        else:
            logger.info(res.json)

        await dialog_manager.start(
            state=StartSG.main_menu,
            mode=StartMode.RESET_STACK
        )

    except Exception as e:
        logger.error(e, exc_info=True)
        await dialog_manager.start(
            state=ErrorsSG.api_error,
            mode=StartMode.RESET_STACK,
            data={'error_text': str(e)}
        )


# Menu commands ------------------------------------------------------------------------------------------------------------
@router.callback_query(F.data == 'menu')
@router.message(Command(commands=['menu']))
async def process_menu_update(update: Message | CallbackQuery, dialog_manager: DialogManager):
    if isinstance(update, CallbackQuery):
        await update.message.chat.do('typing')
    else:  # if Message
        await update.chat.do('typing')

    await dialog_manager.start(StartSG.main_menu, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['recipes']))
async def process_recipes_command(message: Message, dialog_manager: DialogManager):
    await message.chat.do('typing')
    await dialog_manager.start(RecipesSG.recipes_main_menu, mode=StartMode.RESET_STACK)


@catch_api_error
@router.message(Command(commands=['selections']))
async def process_selections_command(message: Message, dialog_manager: DialogManager):
    await message.chat.do('typing')
    selections: list[dict] = await django_api.get_all_products_selections()
    await dialog_manager.start(
        state=SelectionsSG.all_selections,
        data={'selections': selections},
        mode=StartMode.RESET_STACK
    )


# User unsubscribed -----------------------------------------------------------------------------------------------
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_unsubscribing(chat_member_update: ChatMemberUpdated):
    await django_api.unsubscribe_user(chat_member_update.from_user.id)
    logger.info(f'Пользователь [{chat_member_update.from_user.id}#'
                f'{chat_member_update.from_user.username}] отписался от бота')
























