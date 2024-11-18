from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import Message, CallbackQuery, TelegramObject, User, Chat

from cachetools import TTLCache
import logging

# from database.database import AsyncDatabase

MESSAGE_THROTTLING_CACHE = TTLCache(maxsize=10_000, ttl=1)  # Макс размер кэша - 10000 ключей, время жизни ключа - 2 секунд
CALLBACK_THROTTLING_CACHE = TTLCache(maxsize=10_000, ttl=0.5)
ANTIFLOOD_CACHE = TTLCache(maxsize=1_000, ttl=60)

logger = logging.getLogger(__name__)


class CheckChatPrivacyMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        chat: Chat = data.get('event_chat')

        if chat.type != 'private':  # ignore group chats, supergroups and channels
            user: User = data.get('event_from_user')
            if user:
                logger.warning(f'User [{user.id}#{user.username}] tried to call bot in group chat (chat_id={chat.id})')
            else:
                logger.warning(f'Somebody tried to call bot in group chat (chat_id={chat.id})')

            return None

        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):  # outer

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:

        user: User = data.get('event_from_user')

        # get update data
        if isinstance(event, Message):
            msg = event.text
            cache = MESSAGE_THROTTLING_CACHE
        elif isinstance(event, CallbackQuery):
            msg = event.data
            cache = CALLBACK_THROTTLING_CACHE
        else:
            return await handler(event, data)

        # check in cache
        if user.id in cache:
            logger.warning(f'Throttled! user=[{user.id}#{user.username}], event={type(event)}, data={msg}')
            return
        else:
            cache[user.id] = True

        return await handler(event, data)


class AntifloodMiddleware(BaseMiddleware):  # inner

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:

        handler_obj: HandlerObject = data.get('handler')

        if handler_obj.callback.__name__ == 'process_other_updates':
            user: User = data.get('event_from_user')
            if isinstance(event, Message):
                msg_text = event.text
            else:
                msg_text = 'callback_data'

            # TODO: в разраотке. Пока блокировки не будет, о флаг в БД установится. Можно будет вручную потом посмотреть
            if user.id in ANTIFLOOD_CACHE:
                ANTIFLOOD_CACHE[user.id] += 1
                bot: Bot = data.get('bot')

                if ANTIFLOOD_CACHE[user.id] == 3:
                    logger.warning(f'Antiflood! First warning for user=[{user.id}#{user.username}], msg_text={msg_text}')
                    await bot.send_message(
                        chat_id=user.id,
                        text='Уважаемый пользователь,\n'
                             'используйте предложенный функционал бота!\n\n'
                             'Не шлите в бот "спам" сообщения '
                             'во избежание <b>БЛОКИРОВКИ</b>! 😬'
                    )
                    return

                # elif ANTIFLOOD_CACHE[user.id] == 5:
                #     await bot.send_message(
                #         chat_id=user.id,
                #         text='Уважаемый пользователь,\n'
                #              'после следующего "спам" сообщения '
                #              'вы будете заблокированы! 😵'
                #     )
                #     logger.warning(f'Antiflood! Second warning for user={user.id}, msg_text={msg_text}')
                #     return

                # elif ANTIFLOOD_CACHE[user.id] == 6:
                #     await bot.send_message(
                #         chat_id=user.id,
                #         text='Ваш аккаунт был <b>заблокирован</b>!\n'
                #              'Для разблокировки обратитесь в поддержку!'
                #     )
                #
                #     async with AsyncDatabase() as db:
                #         await db.block_user(user.id)
                #         logger.warning(f'Antiflood! User was BLOCKED user={user.id}, msg_text={msg_text}')
                #
                #         dp: Dispatcher = data.get('dispatcher')
                #         workflow_data: dict = dp.workflow_data
                #         workflow_data['blocked_users_ids'] = await db.get_blocked_users_tg_ids()
                #         print(workflow_data)
                #         dp.workflow_data.update(workflow_data)
                #         return

                # TODO: return!!!
                # elif ANTIFLOOD_CACHE[user.id] == 6:
                #     async with AsyncDatabase() as db:
                #         logger.warning(f'Antiflood! User was BLOCKED user=[{user.id}#{user.username}], '
                #                        f'msg_text={msg_text}')
                #         await db.block_user(user.id)
                #         return

                else:
                    return await handler(event, data)

            else:
                ANTIFLOOD_CACHE[user.id] = 1

        return await handler(event, data)



