import asyncio
import logging
from datetime import datetime
import setproctitle

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from lexicon.lexicon import LEXICON
from config_data.config import Config, load_config
from handlers import user_handlers, other_handlers, admin_handlers
from errors import errors_handlers
from keyboards.main_menu import set_main_menu
from middlewares.middlewares import InnerLogHandlerMiddleware, PrepareUpdateMiddleware
from middlewares.spam_limiters import ThrottlingMiddleware, AntifloodMiddleware, CheckChatPrivacyMiddleware
from middlewares.is_admin import AdminAndStaffPassOnlyMiddleware
from utils.admin_utils import send_msg_to_admins_by_api, send_bot_started_msg_to_admins, get_bot_info
# from database.database import AsyncDatabase
from dialogs import user_dialogs, admin_dialogs


logger = logging.getLogger(__name__)


async def main() -> None:

    # Конфиг бота
    cfg: Config = load_config()

    # -- logging
    cfg.setup_logging('./logs')
    logger.info('Starting bot')

    # -- bot, dp
    bot = Bot(
        token=cfg.tg_bot.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher(
        storage=MemoryStorage()
    )

    # -- scheduler
    scheduler = AsyncIOScheduler(timezone=datetime.now().astimezone().tzinfo)
    scheduler.start()

    # Workflow data
    dp.workflow_data.update({
        'admin_ids': cfg.tg_bot.admin_ids,
        'staff_ids': cfg.tg_bot.staff_ids,
        'scheduler': scheduler,
        'debug': cfg.tg_bot.debug,
        # 'blocked_users_ids': await db.get_blocked_users_tg_ids(),
    })

    # ====================== MIDDLEWARES =================================
    # -- admin only
    if cfg.env != 'PROD':
        dp.update.outer_middleware(AdminAndStaffPassOnlyMiddleware())
    # -- prepare update for inner log
    dp.update.outer_middleware(PrepareUpdateMiddleware())
    # -- ignore group chat messages
    dp.update.outer_middleware(CheckChatPrivacyMiddleware())

    # -- throttling
    if cfg.env == 'PROD':
        dp.message.outer_middleware(ThrottlingMiddleware())
        dp.callback_query.outer_middleware(ThrottlingMiddleware())
    # -- log all new updates (total 22 types)
    update_types = [
        dp.message,
        dp.edited_message,
        dp.channel_post,
        dp.edited_channel_post,
        dp.inline_query,
        dp.chosen_inline_result,
        dp.callback_query,
        dp.shipping_query,
        dp.pre_checkout_query,
        dp.poll,
        dp.poll_answer,
        dp.my_chat_member,
        dp.chat_member,
        dp.chat_join_request,
        dp.message_reaction,
        dp.message_reaction_count,
        dp.chat_boost,
        dp.removed_chat_boost,
        # dp.deleted_business_messages,
        # dp.business_connection,
        # dp.edited_business_message,
        # dp.business_message,  # Ошибка при использовании этого апдейта
    ]
    for update_type in update_types:
        update_type.middleware(InnerLogHandlerMiddleware())

    # -- control flood for PROD
    if cfg.env == 'PROD':
        dp.message.middleware(AntifloodMiddleware())
        dp.callback_query.middleware(AntifloodMiddleware())

    # ====================== END MIDDLEWARES =========================================

    # ====================== ROUTERS ==================================================

    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    dp.include_routers(
        # user dialogs
        user_dialogs.main_menu_dialog,
        user_dialogs.recipes_dialog,
        user_dialogs.selections_dialog,
        user_dialogs.errors_dialog,
        # admin dialogs
        admin_dialogs.admin_menu_dialog,
        admin_dialogs.broadcast_dialog,
        admin_dialogs.scheduled_jobs_dialog,
    )
    setup_dialogs(dp)

    dp.include_router(other_handlers.router)

    dp.include_router(errors_handlers.router)

    # ====================== END ROUTERS =============================================

    # Start
    async def on_startup(bot: Bot) -> None:
        # Полное, краткое описания бота
        await bot.set_my_description(
            description=LEXICON.description_text
        )

        await bot.set_my_short_description(
            short_description=LEXICON.short_description_text
        )

        # Меню команд
        await set_main_menu(bot)

        # Сообщения для админов, что бот запущен
        await send_bot_started_msg_to_admins(
            bot=bot,
            admins_ids=cfg.tg_bot.admin_ids
        )

    dp.startup.register(on_startup)

    # Пропускаем старые апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        send_msg_to_admins_by_api(
            bot_token=cfg.tg_bot.token,
            admins_ids=cfg.tg_bot.admin_ids,
            text=f'Admin 👨🏻‍💼:\n\n'
                 f'⭕️ <b>Ошибка запуска бота</b>:\n\n{str(e)}'
        )
        logger.error(f'[Bot Starting Error] - {e}', exc_info=True)
        raise
    finally:
        await bot.session.close()


# Enter Point
if __name__ == "__main__":
    # установка имени процесса для диспетчера процессов
    setproctitle.setproctitle('python__zhzhgis_recipes_bot')

    config: Config = load_config()
    stop_text = '✅ Плановое отключение бота'
    try:
        asyncio.run(main(), debug=config.tg_bot.debug)  # добавление main в цикл событий
    except Exception as ex:
        stop_text = f'<b>Ошибка</b>:\n\n{str(ex)}'
        logger.error(f'[Bot Fatal Error] - {ex}', exc_info=True)
    finally:
        bot_info: dict = get_bot_info(config.tg_bot.token)
        send_msg_to_admins_by_api(
            bot_token=config.tg_bot.token,
            admins_ids=config.tg_bot.admin_ids,
            text=f'Admin 👨🏻‍💼:\n\n'
                 f'⛔️ Бот <b>{bot_info["first_name"]}</b> остановлен! ⛔️\n\n'
                 f'{stop_text}'
        )
        logger.warning(f'!!! Bot stopped !!!')
