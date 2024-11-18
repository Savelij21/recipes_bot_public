import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject, User, Update

logger = logging.getLogger(__name__)


class PrepareUpdateMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        data['update_id'] = event.update_id  # For InnerLogHandlerMiddleware

        return await handler(event, data)


class InnerLogHandlerMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        update_id = data.get('update_id')  # from PrepareUpdateMiddleware
        # для типа Update будет общий для всех хэндлер, поэтому нужной каждый тип апдейта
        # регать в этой миддлвари, чтобы выводился именно его хэндлер
        handler_obj: HandlerObject = data.get('handler')
        user: User = data.get('event_from_user')

        logger.info(
            f'New update: '
            f'update_id={update_id}, '
            f'user=[{user.id}#{user.username}], '
            f'event_type={event.__class__.__name__}, '
            f'handler={handler_obj.callback.__name__}'
        )

        return await handler(event, data)



