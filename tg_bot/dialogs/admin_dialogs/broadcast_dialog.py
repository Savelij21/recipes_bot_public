import pprint

from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, Button, Column, SwitchTo, Start
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.api.entities import MediaAttachment, MediaId

import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from states.dialogs.admin_dialogs_states import AdminModeBroadcastDialogSG, AdminModeScheduledJobsDialogSG
from filters.is_admin import IsAdmin
from utils.broadcaster_util import broadcast_start
from utils.admin_utils import get_broadcast_time_left_text
from external_services import django_api


logger = logging.getLogger(__name__)


# ========================================= BROADCAST TEXT WINDOWS ===============================================
# Handlers -----------------------------
async def process_newsletter_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.chat.do('typing')
    dialog_manager.dialog_data.update({'text': message.text})
    msg = await message.answer('Ваш текст для рассылки:')
    await asyncio.sleep(1)
    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.check_text)
    await msg.delete()


async def process_newsletter_text_invalid(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.chat.do('typing')
    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.invalid_text)


async def process_newsletter_text_success(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await callback.message.chat.do('typing')
    await callback.message.edit_text('Текст рассылки сохранен ☑️')
    await asyncio.sleep(1)
    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.add_image_or_not)


# Getters ----------------------
async def newsletter_input_text_getter(dialog_manager: DialogManager, *args, **kwargs):
    return {'text': dialog_manager.dialog_data.get('text')}


# Windows ---------------------
text_input_window: Window = Window(
    Const('Введите <b>текст</b> для рассылки.\n'
          'Для форматирования текста используйте <b>теги</b>:\n\n\n'
          '&lt;b&gt;жирный&lt;/b&gt; - <b>жирный</b>\n\n'
          '&lt;i&gt;курсив&lt;/i&gt; - <i>курсив</i>\n\n'
          '&lt;u&gt;подчеркнутый&lt;/u&gt; - <u>подчеркнутый</u>\n\n'
          '&lt;s&gt;перечеркнутый&lt;s&gt; - <s>перечеркнутый</s>\n\n'
          '&lt;tg-spoiler&gt;скрытый текст&lt;/tg-spoiler&gt; - <tg-spoiler>скрытый текст</tg-spoiler>\n\n'
          '&lt;a href="https://smth.com"&gt;ссылка&lt;/a&gt; - <a href="https://smth.com">ссылка</a>\n'),
    MessageInput(
        func=process_newsletter_text,
        content_types=ContentType.TEXT
    ),
    MessageInput(
        func=process_newsletter_text_invalid,
        content_types=ContentType.ANY
    ),
    Cancel(
        text=Const('⬅️ В админ меню'),
        id='back_to_admin_menu',
    ),
    state=AdminModeBroadcastDialogSG.start,
)

check_text_window: Window = Window(
    Format('{text}'),
    Column(
        Button(
            text=Const('Продолжить ➡️'),
            id='continue',
            on_click=process_newsletter_text_success
        ),
        SwitchTo(
            text=Const('Редактировать ✏️'),
            id='edit',
            state=AdminModeBroadcastDialogSG.edit_text
        ),
        SwitchTo(
            text=Const('✖️ Отменить рассылку'),
            id='cancel',
            state=AdminModeBroadcastDialogSG.cancel
        )
    ),
    state=AdminModeBroadcastDialogSG.check_text,
    getter=newsletter_input_text_getter
)

edit_text_window: Window = Window(
    Const('<b>Скопируйте отправленный вами ранее текст и отредактируйте.</b>\n'
          'Для форматирования текста используйте <b>теги</b>:\n\n\n'
          '&lt;b&gt;жирный&lt;/b&gt; - <b>жирный</b>\n\n'
          '&lt;i&gt;курсив&lt;/i&gt; - <i>курсив</i>\n\n'
          '&lt;u&gt;подчеркнутый&lt;/u&gt; - <u>подчеркнутый</u>\n\n'
          '&lt;s&gt;перечеркнутый&lt;s&gt; - <s>перечеркнутый</s>\n\n'
          '&lt;tg-spoiler&gt;скрытый текст&lt;/tg-spoiler&gt; - <tg-spoiler>скрытый текст</tg-spoiler>\n\n'
          '&lt;a href="https://smth.com"&gt;ссылка&lt;/a&gt; - <a href="https://smth.com">ссылка</a>\n'),
    MessageInput(
        func=process_newsletter_text,
        content_types=ContentType.TEXT
    ),
    MessageInput(
        func=process_newsletter_text_invalid,
        content_types=ContentType.ANY
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.edit_text
)

invalid_text_window: Window = Window(
    Const('Пожалуйста, введите <b>текст</b> для рассылки:'),
    MessageInput(
        func=process_newsletter_text,
        content_types=ContentType.TEXT
    ),
    MessageInput(
        func=process_newsletter_text_invalid,
        content_types=ContentType.ANY
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.invalid_text
)


# ================================ IMAGE ADDING WINDOWS ====================================================
# Handlers ----------------------
async def process_add_image(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.chat.do('typing')
    dialog_manager.dialog_data.update({'file_id': message.photo[-1].file_id})
    msg = await message.answer('Изображение для рассылки сохранено ☑️')
    await asyncio.sleep(2)
    await msg.edit_text('Конечный вид рассылки:')
    await asyncio.sleep(2)
    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.finish_view)
    await msg.delete()


async def process_add_image_invalid(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.chat.do('typing')
    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.invalid_image)


async def process_finish_view(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await callback.message.chat.do('typing')
    await callback.message.edit_text('Конечный вид рассылки:')
    await asyncio.sleep(2)
    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.finish_view)


# Getters -----------------------

# Windows -----------------------
add_img_or_not_window: Window = Window(
    Const('Нужно ли добавить изображение? 🖼'),
    SwitchTo(
        text=Const('Добавить ↗️'),
        id='add_image',
        state=AdminModeBroadcastDialogSG.add_image
    ),
    Button(
        text=Const('Без изображения ➡️'),
        id='no_image',
        on_click=process_finish_view
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.add_image_or_not
)

upload_img_window: Window = Window(
    Const('Загрузите изображение для рассылки:'),
    MessageInput(
        func=process_add_image,
        content_types=ContentType.PHOTO
    ),
    MessageInput(
        func=process_add_image_invalid,
        content_types=ContentType.ANY
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.add_image
)

invalid_img_window: Window = Window(
    Const('Пожалуйста, загрузите <b>изображение</b> для рассылки:'),
    MessageInput(
        func=process_add_image,
        content_types=ContentType.PHOTO
    ),
    MessageInput(
        func=process_add_image_invalid,
        content_types=ContentType.ANY
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.invalid_image
)


# =========================================== FINISH VIEW WINDOWS ===================================================
# Handlers --------------------
async def start_broadcast_now(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await broadcast_start(
        admin_id=callback.from_user.id,
        bot=callback.bot,
        text=dialog_manager.dialog_data.get('text'),
        image=dialog_manager.dialog_data.get('file_id'),
        state=dialog_manager.middleware_data.get('state')
    )
    # переходим от диалогов к хэндлерам
    await dialog_manager.reset_stack()


# Getters ---------------------
async def finish_view_getter(dialog_manager: DialogManager, *args, **kwargs):
    image_file_id = dialog_manager.dialog_data.get('file_id')
    if image_file_id:
        image = MediaAttachment(
            type=ContentType.PHOTO,
            file_id=MediaId(image_file_id)
        )
    else:
        image = None

    return {
        'image': image,
        'text': dialog_manager.dialog_data.get('text')
    }


async def finish_creation_getter(dialog_manager: DialogManager, *args, **kwargs):
    users_stats = await django_api.get_users_stats()

    return {
        'all': users_stats['all'],
        'subscribed': users_stats['subscribed'],
        'unsubscribed': users_stats['unsubscribed'],
        'send_time': get_broadcast_time_left_text(users_stats['subscribed'])
    }


# Windows ---------------------
finish_view_window: Window = Window(
    DynamicMedia(
        selector='image',
        when='image'
    ),
    Format(
        text='{text}'
    ),
    SwitchTo(
        text=Const('Готово к рассылке 📩'),
        id='ready_to_send',
        state=AdminModeBroadcastDialogSG.finish_creation
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.finish_view,
    getter=finish_view_getter
)

creation_type_window: Window = Window(
    Format('Пользователей в базе: <b>{all}</b>\n'
           '<u>Активные</u>: <b>{subscribed}</b>\n'
           '<u>Неактивные</u>: <b>{unsubscribed}</b>\n\n'
           'Рассылка будет отправлена только <u>активным</u> пользователям.\n'
           'Расчетное время отправки: <b>{send_time}</b>'),
    SwitchTo(
        text=Const('Запланировать рассылку ⏰'),
        id='schedule_broadcast',
        state=AdminModeBroadcastDialogSG.input_schedule_time
    ),
    Button(
        text=Const('Начать рассылку 📨'),
        id='start_broadcast',
        on_click=start_broadcast_now
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.finish_creation,
    getter=finish_creation_getter
)


# =========================================== SCHEDULING WINDOWS ===================================================
# Handlers -------------------
async def process_time_input(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.chat.do('typing')

    try:
        dt = datetime.strptime(
            f'{datetime.now().strftime("%Y-%m-%d")} {message.text}',
            '%Y-%m-%d %H:%M'
        )
    except ValueError:
        msg = await message.answer('Некорректное время!')
        await asyncio.sleep(2)
        await msg.delete()
        return

    if dt < datetime.now():
        msg = await message.answer('Введите корректное время!')
        await asyncio.sleep(2)
        await msg.delete()
        return

    dialog_manager.dialog_data.update({'schedule_time': dt})
    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.check_schedule_time)


async def schedule_broadcast(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    schedule_time: datetime = dialog_manager.dialog_data.get('schedule_time')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')

    scheduler.add_job(
        id=f'schedule_broadcast__{(schedule_time.strftime("%Y%m%d_%H%M%S"))}',
        func=broadcast_start,
        trigger='date',
        run_date=schedule_time,
        kwargs={
            'admin_id': callback.from_user.id,
            'bot': callback.bot,
            'text': dialog_manager.dialog_data.get('text'),
            'image': dialog_manager.dialog_data.get('file_id'),
            'state': dialog_manager.middleware_data.get('state')
        }
    )

    logger.info(f'Запланирована рассылка на следующее время: {schedule_time.strftime("%Y-%m-%d %H:%M:%S")}')

    await dialog_manager.switch_to(AdminModeBroadcastDialogSG.scheduled_broadcast_registered)
    return


# Getters ----------------------
async def check_schedule_time_getter(dialog_manager: DialogManager, *args, **kwargs):
    schedule_time: datetime = dialog_manager.dialog_data.get('schedule_time')
    time_left = round((schedule_time - datetime.now()).total_seconds())
    return {
        'schedule_time': schedule_time.strftime("%d.%m.%Y %H:%M"),
        'left_hours': time_left // 3600,
        'left_minutes': (time_left % 3600) // 60,
        'left_seconds': (time_left % 3600) % 60
    }


async def scheduled_broadcast_registered_getter(dialog_manager: DialogManager, *args, **kwargs):
    return {
        'schedule_time': dialog_manager.dialog_data.get('schedule_time')
    }


# Windows -----------------------
schedule_time_input_window: Window = Window(
    Const('Введите время для сегодняшней рассылки по МСК (пример: 13:45):'),
    MessageInput(
        func=process_time_input,
        content_types=ContentType.TEXT
    ),
    state=AdminModeBroadcastDialogSG.input_schedule_time
)

check_schedule_time_window: Window = Window(
    Format(
        'Планируемое время: {schedule_time}\n'
        '(через {left_hours} часов, {left_minutes} минут, {left_seconds} секунд)'
    ),
    Button(
        text=Const('Запланировать'),
        id='schedule',
        on_click=schedule_broadcast
    ),
    SwitchTo(
        text=Const('✖️ Отменить рассылку'),
        id='cancel',
        state=AdminModeBroadcastDialogSG.cancel
    ),
    state=AdminModeBroadcastDialogSG.check_schedule_time,
    getter=check_schedule_time_getter
)

success_schedule_window: Window = Window(
    Format('Рассылка запланирована на {schedule_time} ⏳'),
    Start(
        text=Const('Запланированные рассылки'),
        id='go_to_broadcast_scheduled_jobs',
        state=AdminModeScheduledJobsDialogSG.broadcast_jobs
    ),
    Cancel(
        text=Const('⬅️ В админ меню'),
        id='back_to_admin_menu',
    ),
    state=AdminModeBroadcastDialogSG.scheduled_broadcast_registered,
    getter=scheduled_broadcast_registered_getter
)


# ================================================ CANCELLED BROADCASTING WINDOW ================================
# Handlers -------------

# Getters ---------------

# Window ----------------
canceled_broadcasting: Window = Window(
    Const('Рассылка отменена ❌'),
    Cancel(
        text=Const('⬅️ В админ меню'),
        id='back_to_admin_menu',
    ),
    state=AdminModeBroadcastDialogSG.cancel
)


# =============================================== DIALOG ==================================================
broadcast_dialog = Dialog(
    # text input
    text_input_window,
    check_text_window,
    edit_text_window,
    invalid_text_window,
    # image
    add_img_or_not_window,
    upload_img_window,
    invalid_img_window,
    # finish view
    finish_view_window,
    creation_type_window,
    # schedule
    schedule_time_input_window,
    check_schedule_time_window,
    success_schedule_window,
    # cancel
    canceled_broadcasting
)


# Filters -------------------------------
broadcast_dialog.message.filter(IsAdmin())
broadcast_dialog.callback_query.filter(IsAdmin())
