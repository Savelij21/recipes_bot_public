from datetime import datetime, timedelta
from typing import List, Tuple
import requests
from aiogram import Bot
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def get_bot_info(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['result']
    else:
        # Обработка ошибки, если запрос не удался
        print("Ошибка при выполнении запроса:", response.status_code)
        return None


def send_msg_to_admins_by_api(bot_token: str, admins_ids: List[int], text: str = '') -> None:
    for admin_id in admins_ids:
        requests.post(
            url=f'https://api.telegram.org/bot{bot_token}/sendMessage',
            data={
                'chat_id': admin_id,
                'text': text,
                'parse_mode': 'HTML'
            }
        )


async def send_bot_started_msg_to_admins(bot: Bot, admins_ids: List[int]) -> None:
    bot_info = await bot.get_me()
    for admin_id in admins_ids:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=f'Admin 👨🏻‍💼:\n\n'
                     f'🚀 Бот <b>{bot_info.first_name}</b> успешно запущен! 🚀'
            )
        except Exception as e:
            print(e)
            continue


# BROADCAST ------------------------------------------------------------------------------
def get_broadcast_time_left_text(users_amount: int) -> str:
    if users_amount * 0.2 < 60:
        return f'~{round(users_amount * 0.2, 1)} секунд'
    else:
        return f'~{round(users_amount * 0.2 / 60)} минут'


# SCHEDULING -----------------------------------------------------------------------------
def get_scheduled_broadcast_jobs(scheduler: AsyncIOScheduler) -> Tuple[Job]:
    return tuple(filter(lambda job: 'schedule_broadcast' in job.id, scheduler.get_jobs()))


def get_scheduled_other_jobs(scheduler: AsyncIOScheduler) -> Tuple[Job]:
    return tuple(filter(lambda job: 'schedule_broadcast' not in job.id, scheduler.get_jobs()))


def prepare_scheduled_job_data(job: Job) -> dict:
    next_run_time: datetime = datetime.strptime(job.next_run_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    time_left: timedelta = next_run_time - datetime.now()
    return {
        'job': job,
        'time_left': {
            'hours': time_left.seconds // 3600,
            'minutes': time_left.seconds % 3600 // 60,
            'seconds': time_left.seconds % 3600 % 60
        }
    }
