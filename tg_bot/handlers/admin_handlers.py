
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode

from asyncio import Task
import logging

from filters.is_admin import IsAdmin
from keyboards.admin_keyboards import (get_back_to_admin_menu_kb, get_confirm_stop_broadcast_kb, get_broadcast_process_kb)
from states.dialogs.admin_dialogs_states import AdminModeMenuDialogSG

router = Router()

logger = logging.getLogger(__name__)


# FOR TESTS ======================================================================================================
# @router.message(IsAdmin(), Command(commands=['test']))
# async def process_test_command(message: Message):
#     await message.chat.do('typing')
#     # await message.answer_video_note(
#     #     video_note=FSInputFile('sources/circles/test_circle_2.mp4')
#     # )
#     await message.answer(
#         text=message.from_user.url
#     )


# ================================================================================================================


# /admin ----------------------------------------------------------
@router.callback_query(F.data == 'admin', IsAdmin())
@router.message(Command(commands=['admin']), IsAdmin())
async def process_admin_command(update: CallbackQuery | Message, dialog_manager: DialogManager, *args, **kwargs):
    if isinstance(update, CallbackQuery):
        await update.message.chat.do('typing')
    else:  # if Message
        await update.chat.do('typing')

    await dialog_manager.start(AdminModeMenuDialogSG.start, mode=StartMode.RESET_STACK)


# Broadcast cancelling ------------------------------------------------
@router.callback_query(F.data == 'stop_broadcast', IsAdmin())
async def process_callback_stop_broadcast(callback: CallbackQuery, state: FSMContext):
    # Убираем у сообщения процессы рассылки кнопку и кидаем объект сообщения в стейт для последующего обновления
    broadcast_process_msg = await callback.message.edit_reply_markup(None)
    await state.update_data(broadcast_process_msg=broadcast_process_msg)
    await callback.message.answer(
        text='Остановить рассылку? ⭕️',
        reply_markup=get_confirm_stop_broadcast_kb()
    )


@router.callback_query(F.data == 'confirm_stop_broadcast', IsAdmin())
async def process_callback_confirm_stop_broadcast(callback: CallbackQuery, state: FSMContext):
    # достаем из стейта объект задачи рассылки, останавливаем задачу, чистим стейт
    state_data = await state.get_data()
    broadcast_task: Task = state_data.get('broadcast_task')

    if broadcast_task:
        broadcast_task.cancel()
        logger.warning(f'Рассылка остановлена пользователем '
                       f'{callback.from_user.id}#{callback.from_user.username}')
        await callback.message.edit_text(
            text='Рассылка остановлена ⭕️',
            reply_markup=get_back_to_admin_menu_kb()
        )
    else:
        logger.warning(f'Задача рассылки для отмены не найдена в стейте')
        await callback.message.edit_text(
            text='Задача рассылки не найдена...',
            reply_markup=get_back_to_admin_menu_kb()
        )

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == 'cancel_stop_broadcast', IsAdmin())
async def process_callback_cancel_stop_broadcast(callback: CallbackQuery, state: FSMContext):
    # удаляем сообщение для отмены, возвращаем сообщению процесса рассылки клавиатуру
    await callback.message.delete()
    state_data = await state.get_data()
    broadcast_process_msg: Message = state_data.get('broadcast_process_msg')
    await broadcast_process_msg.edit_reply_markup(
        reply_markup=get_broadcast_process_kb()
    )

