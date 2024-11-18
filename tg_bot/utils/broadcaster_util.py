
from aiogram import Bot
from aiogram import exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

import asyncio
import logging
from asyncio import Task
from typing import Union
from datetime import datetime

from keyboards.admin_keyboards import get_back_to_admin_menu_kb, get_broadcast_process_kb
from utils.admin_utils import get_broadcast_time_left_text
from external_services import django_api


logger = logging.getLogger(__name__)

# Переменные для аналитики
unsubscribed: int
flood_limits: int
with_errors: int


async def _send_message(
    bot: Bot,
    user_id: Union[int, str],
    text: str,
    image: str = None,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
) -> bool:

    global unsubscribed
    global flood_limits
    global with_errors

    try:
        if not image:
            await bot.send_message(
                chat_id=user_id,
                text=text,
                disable_notification=disable_notification,
                reply_markup=reply_markup,
            )
        else:
            await bot.send_photo(
                chat_id=user_id,
                photo=image,
                caption=text,
                disable_notification=disable_notification,
                reply_markup=reply_markup,
            )

    except exceptions.TelegramBadRequest as e:
        logging.error(f"Telegram server says - Bad Request: {e}")
        await django_api.unsubscribe_user(user_id)
        logger.warning(f'Подписка отменена для {user_id}')
        with_errors += 1

    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError - may be unsubscribed")
        await django_api.unsubscribe_user(user_id)
        logger.warning(f'Подписка отменена для {user_id}')
        unsubscribed += 1

    except exceptions.TelegramRetryAfter as e:
        logging.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        flood_limits += 1
        return await _send_message(
            bot, user_id, text, image, disable_notification, reply_markup
        )  # Recursive call

    except exceptions.TelegramAPIError as e:
        logging.exception(f"Target [ID:{user_id}] failed: {e}")
        await django_api.unsubscribe_user(user_id)
        logger.warning(f'Подписка отменена для {user_id}')
        with_errors += 1

    except Exception as e:
        logging.exception(f"Unknown error for [ID:{user_id}]: {e}")
        with_errors += 1

    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True

    return False


async def _broadcast(
    admin_id: int,
    bot: Bot,
    text: str,
    image: str = None,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
):

    # prepare
    # TODO: users and recipes?? backup on django!

    # except Exception as ex:
    #     logger.error(str(ex), exc_info=True)
    #     await bot.send_message(
    #         chat_id=admin_id,
    #         text=f'Не удалось создать резервную копию базы данных ❌\n'
    #              f'Создание рассылки отменено ❌\n\n'
    #              f'{ex}',
    #         reply_markup=get_back_to_admin_menu_kb()
    #     )
    #     return

    # else:
    #     await bot.send_message(
    #         chat_id=admin_id,
    #         text='Резервная копия базы данных сохранена в директории бота и на Yandex Cloud ☑️',
    #     )

    # await asyncio.sleep(1)

    # register and reset global parameters
    global unsubscribed
    global flood_limits
    global with_errors

    unsubscribed = 0
    flood_limits = 0
    with_errors = 0

    # prepare variables for results analyze
    start_time = datetime.now()
    success_count = 0
    total_count = 0
    users_tg_ids: list[int] = await django_api.get_active_users_tg_ids()
    total_users = len(users_tg_ids)

    logger.info(f'Запущена рассылка для {len(users_tg_ids)} пользователей')

    text_template: str = (
        '{header}\n\n'
        'Обработано {total_count} из {total_users} пользователей.\n'
        'Доставлено ✅: {success_count}\n'
        'Отписались 🚫: {unsubscribed}\n'
        'Не доставлено по другим причинам ⁉️: {with_errors}\n'
        'Оставшееся время: {time_left}'
    )

    process_msg = await bot.send_message(
        chat_id=admin_id,
        text=text_template.format(
            header='<b>Рассылка запущена</b> ⏳',
            total_count=total_count,
            total_users=total_users,
            success_count=success_count,
            unsubscribed=unsubscribed,
            with_errors=with_errors,
            time_left=get_broadcast_time_left_text(users_amount=total_users - total_count)
        ),
        reply_markup=get_broadcast_process_kb()
    )

    try:
        for user_id in users_tg_ids:
            total_count += 1
            if await _send_message(
                bot, user_id,
                text, image,
                disable_notification,
                reply_markup
            ):
                success_count += 1

            if total_count % 20 == 0 or total_count == total_users:
                await bot.edit_message_text(
                    chat_id=admin_id,
                    message_id=process_msg.message_id,
                    text=text_template.format(
                        header='<b>Рассылка запущена</b> ⏳',
                        total_count=total_count,
                        total_users=total_users,
                        success_count=success_count,
                        unsubscribed=unsubscribed,
                        with_errors=with_errors,
                        time_left=get_broadcast_time_left_text(users_amount=total_users - total_count)
                    ),
                    reply_markup=get_broadcast_process_kb()
                )
    finally:
        logging.info(f"{success_count} messages successful sent.")

    time_delta = round((datetime.now() - start_time).total_seconds(), 3)
    results = {
        'total_sec': time_delta,
        'sec_per_user': time_delta / total_users,
        'msg_per_sec': 1 / (time_delta / total_users),
        'sent': total_users,
        'success': success_count,
        'unsubscribed': unsubscribed,
        'flood_limits': flood_limits,
        'with_errors': with_errors
    }
    logging.info(f'Рассылка завершена. Результаты: {results}')

    await bot.edit_message_text(
        chat_id=admin_id,
        message_id=process_msg.message_id,
        text=text_template.format(
            header='<b>Рассылка завершена</b> 🏁',
            total_count=total_count,
            total_users=total_users,
            success_count=success_count,
            unsubscribed=unsubscribed,
            with_errors=with_errors,
            time_left=get_broadcast_time_left_text(users_amount=total_users - total_count)
        ),
        reply_markup=get_back_to_admin_menu_kb()
    )
    return success_count


async def broadcast_start(
        admin_id: int,
        bot: Bot,
        text: str,
        image: str,
        state: FSMContext
):
    # создаем и запускаем задачу на рассылку
    broadcast_task: Task = asyncio.create_task(
        _broadcast(
            admin_id,
            bot,
            text,
            image
        )
    )
    # добавляем в стейт инфу о задаче рассылки
    await state.update_data(broadcast_task=broadcast_task)









