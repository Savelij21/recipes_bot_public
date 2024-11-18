import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

logger = logging.getLogger(__name__)


class AdminAndStaffPassOnlyMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        admin_ids: list[int] = data['admin_ids']
        staff_ids: list[int] = data['staff_ids']

        user: User = data.get('event_from_user')

        if user.id in admin_ids or user.id in staff_ids:
            return await handler(event, data)
        else:
            logger.info(f'Пользователь [{user.id}#{user.username}] попытался воспользоваться ботом')
            return

