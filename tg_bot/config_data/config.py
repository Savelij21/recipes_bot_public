from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from typing import Callable
import logging
from logging.handlers import RotatingFileHandler
import os


PROJECT_DIR = Path(__file__).parent.parent.parent
DOTENV_PATH = os.path.join(PROJECT_DIR, '.env')


@dataclass
class DjangoConfig:
    host: str
    host_api: str
    api_secret_key: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    staff_ids: list[int]
    debug: bool

    def __str__(self):
        return f'token: {self.token}\nadmin_ids: {self.admin_ids}\nstaff_ids: {self.staff_ids}\ndebug: {self.debug}'


@dataclass
class Config:
    tg_bot: TgBot
    setup_logging: Callable[[str], None]
    env: str

    def __str__(self):
        return f'tg_bot: {self.tg_bot}\nenv: {self.env}\nsetup_logging: {self.setup_logging}'


# logging
def setup_logging(logs_dir_path: str = './logs') -> None:
    # Конфиг для логирования
    if not os.path.exists(logs_dir_path):
        os.mkdir(logs_dir_path)

    # Формат логов
    log_format = '[%(asctime)s] [%(levelname)s] - %(name)s - %(message)s (%(filename)s:%(lineno)d)'

    # Хэндлеры для общего лога
    common_file_handler = RotatingFileHandler(
        filename=os.path.join(logs_dir_path, 'bot.log'),
        maxBytes=16 * 1024 * 1024,  # 16 MB
        backupCount=5,
        encoding='utf-8'
    )
    common_file_handler.setLevel(logging.INFO)

    # Хэндлер для вывода логов в консоль
    console_stream_handler = logging.StreamHandler()
    console_stream_handler.setLevel(logging.INFO)

    # Хэндлер для логов ошибок
    error_file_handler = RotatingFileHandler(
        filename=os.path.join(logs_dir_path, 'error.log'),
        maxBytes=16 * 1024 * 1024,  # 16 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)

    # Итоговый конфиг
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            common_file_handler,
            console_stream_handler,
            error_file_handler
        ]
    )

    # Для asyncio логов даем уровень только ERROR, а то спамит предупреждениями
    logging.getLogger('asyncio').setLevel(logging.ERROR)


# config
def load_config() -> Config:
    load_dotenv(DOTENV_PATH)

    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN'),
            admin_ids=[int(tg_id.strip()) for tg_id in os.getenv('ADMIN_IDS').split(',')],
            staff_ids=[int(tg_id.strip()) for tg_id in os.getenv('STAFF_IDS').split(',')],
            debug=os.getenv('DEBUG') == 'True'
        ),
        setup_logging=setup_logging,
        env=os.getenv('ENV')
    )


def get_django_config() -> DjangoConfig:
    load_dotenv(DOTENV_PATH)

    return DjangoConfig(
        host=os.getenv('DJANGO_HOST'),
        host_api=os.getenv('DJANGO_HOST') + '/api',
        api_secret_key=os.getenv('DJANGO_API_SECRET_KEY')
    )

