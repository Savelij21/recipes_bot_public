from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot) -> bool:

    # return await bot.delete_my_commands()

    commands = [
        BotCommand(
            command='/menu',
            description='Главное меню 🗄'
        ),
        BotCommand(
            command='/recipes',
            description='Рецепты 🥣'
        ),
        BotCommand(
            command='/selections',
            description='Подборки продуктов 🛍'
        ),
    ]

    return await bot.set_my_commands(commands)

