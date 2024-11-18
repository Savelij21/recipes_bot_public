
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Column, Cancel, SwitchTo, Select
from aiogram_dialog.widgets.text import Const, Format, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from datetime import datetime
import logging

from states.dialogs.admin_dialogs_states import AdminModeScheduledJobsDialogSG
from filters.is_admin import IsAdmin
from utils.admin_utils import prepare_scheduled_job_data, get_scheduled_broadcast_jobs, get_scheduled_other_jobs

logger = logging.getLogger(__name__)


# ==================================== SCHEDULED JOBS MENU WINDOW ===========================================
# Handlers ---------------

# Getters ----------------
async def scheduled_jobs_menu_getter(dialog_manager: DialogManager, scheduler: AsyncIOScheduler, **kwargs) -> dict:
    jobs: list[Job] = scheduler.get_jobs()
    if not jobs:
        return {'no_jobs': True}
    else:
        return {
            'jobs_amount': len(jobs),
            'broadcast_jobs_amount': len(get_scheduled_broadcast_jobs(scheduler)),
            'other_jobs_amount': len(get_scheduled_other_jobs(scheduler))
        }


# Window -----------------
scheduled_jobs_menu_window: Window = Window(
    Format('Запланированные задачи ({jobs_amount}):', when='jobs_amount'),
    Const('Нет запланированных задач', when='no_jobs'),
    Column(
        SwitchTo(
            text=Format('Рассылки ({broadcast_jobs_amount})'),
            id='broadcast_jobs',
            state=AdminModeScheduledJobsDialogSG.broadcast_jobs
        ),
        SwitchTo(
            text=Format('Другие задачи ({other_jobs_amount})'),
            id='other_jobs',
            state=AdminModeScheduledJobsDialogSG.other_jobs
        ),
        when='jobs_amount'
    ),
    Cancel(
        text=Const('⬅️ Назад'),
        id='cancel',
    ),
    state=AdminModeScheduledJobsDialogSG.start,
    getter=scheduled_jobs_menu_getter
)


# =================================== BROADCAST SCHEDULED JOBS WINDOW ================================================
# Handlers ---------------------
async def process_broadcast_job_selected(callback: CallbackQuery,
                                         widget: Select,
                                         dialog_manager: DialogManager,
                                         job_id: str):
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    dialog_manager.dialog_data.update({'broadcast_job': scheduler.get_job(job_id)})
    await dialog_manager.switch_to(AdminModeScheduledJobsDialogSG.selected_broadcast_job)


# Getters -----------------------
async def broadcast_jobs_getter(dialog_manager: DialogManager, scheduler: AsyncIOScheduler, **kwargs) -> dict:
    broadcast_jobs_data = []
    for (index, job) in enumerate(get_scheduled_broadcast_jobs(scheduler), start=1):
        prepared_data: dict = prepare_scheduled_job_data(job)
        prepared_data['index'] = index
        broadcast_jobs_data.append(prepared_data)

    return {
        'jobs_amount': len(broadcast_jobs_data),
        'jobs': broadcast_jobs_data
    }


# Window ------------------------
scheduled_broadcast_jobs_window: Window = Window(
    Format('<u>Запланированные рассылки</u> ({jobs_amount}):\n'),
    List(
        field=Format(
            '<b>{item[index]})</b> Рассылка плановая #{item[job].id}\n'
            'Запланирована на {item[job].next_run_time}\n'
            '(через {item[time_left][hours]} часов, {item[time_left][minutes]} '
            'минут и {item[time_left][seconds]} секунд)'
        ),
        items='jobs',
        sep='\n\n'
    ),
    Column(
        Select(
            text=Format('{item[index]}) {item[job].id}'),
            id='broadcast_job',
            item_id_getter=lambda item: item['job'].id,
            items='jobs',
            on_click=process_broadcast_job_selected
        )
    ),
    SwitchTo(
        text=Const('⬅️ Назад'),
        id='back',
        state=AdminModeScheduledJobsDialogSG.start
    ),
    state=AdminModeScheduledJobsDialogSG.broadcast_jobs,
    getter=broadcast_jobs_getter
)


# ================================== SELECTED BROADCAST JOB WINDOWS ===========================================
# Handlers ----------------------------
async def process_cancel_broadcast_job(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    job: Job = dialog_manager.dialog_data.get('broadcast_job')
    job.remove()
    logger.info(f'Запланированная задача рассылки {job.id} отменена')
    await dialog_manager.switch_to(AdminModeScheduledJobsDialogSG.canceled_broadcast_job)


# Getters -----------------------------
async def selected_broadcast_job_getter(dialog_manager: DialogManager, scheduler: AsyncIOScheduler, **kwargs) -> dict:
    job: Job = dialog_manager.dialog_data.get('broadcast_job')
    dt = datetime.strptime(job.next_run_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    time_left = dt - datetime.now()
    return {
        'job': job,
        'left_hours': time_left.seconds // 3600,
        'left_minutes': time_left.seconds % 3600 // 60,
        'left_seconds': time_left.seconds % 3600 % 60
    }


# Windows ------------------------------
selected_broadcast_job_window: Window = Window(
    Format(
        '<b>Рассылка плановая</b> #{job.id}\n\n'
        'Запланирована на {job.next_run_time}\n'
        '(через {left_hours} часов, {left_minutes} минут и '
        '{left_seconds} секунд)'
    ),
    Button(
        text=Const('Отменить рассылку ⭕️'),
        id='cancel_broadcast_job',
        on_click=process_cancel_broadcast_job
    ),
    SwitchTo(
        text=Const('⬅️ Назад'),
        id='back',
        state=AdminModeScheduledJobsDialogSG.broadcast_jobs
    ),
    state=AdminModeScheduledJobsDialogSG.selected_broadcast_job,
    getter=selected_broadcast_job_getter
)

cancelled_broadcast_job_window: Window = Window(
    Const('Рассылка отменена ❌'),
    Cancel(
        text=Const('⬅️ В админ меню'),
        id='cancel'
    ),
    state=AdminModeScheduledJobsDialogSG.canceled_broadcast_job
)


# ==================================== OTHER SCHEDULED JOBS WINDOW ==============================================
# Handlers --------------

# Getters ------------------
async def other_jobs_getter(dialog_manager: DialogManager, scheduler: AsyncIOScheduler, **kwargs) -> dict:
    other_jobs_data = []
    for (index, job) in enumerate(get_scheduled_other_jobs(scheduler), start=1):
        dt = datetime.strptime(job.next_run_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_left = dt - datetime.now()

        other_jobs_data.append((
            index,
            job,
            (
                time_left.seconds // 3600,
                time_left.seconds % 3600 // 60,
                time_left.seconds % 3600 % 60
            )
        ))

    return {
        'jobs_amount': len(other_jobs_data),
        'jobs': other_jobs_data
    }


# Window -----------------------------
other_scheduled_jobs_window: Window = Window(
    Format('<u>Остальные запланированные задачи</u> ({jobs_amount}):\n\n'),
    List(
        field=Format(
            '<b>{item[0]})</b> Задача плановая #{item[1].id}\n'
            'Запланирована на {item[1].next_run_time}\n'
            '(через {item[2][0]} часов, {item[2][1]} минут и '
            '{item[2][2]} секунд)'
        ),
        items='jobs',
        sep='\n\n'
    ),
    SwitchTo(
        text=Const('⬅️ Назад'),
        id='back',
        state=AdminModeScheduledJobsDialogSG.start
    ),
    state=AdminModeScheduledJobsDialogSG.other_jobs,
    getter=other_jobs_getter
)


# ============================================= DIALOG =====================================================
scheduled_jobs_dialog = Dialog(
    # all scheduled jobs
    scheduled_jobs_menu_window,
    # broadcast scheduled jobs
    scheduled_broadcast_jobs_window,
    # selected broadcast job
    selected_broadcast_job_window,
    cancelled_broadcast_job_window,
    # other scheduled jobs
    other_scheduled_jobs_window
)

# Filters -------------------
scheduled_jobs_dialog.message.filter(IsAdmin())
scheduled_jobs_dialog.callback_query.filter(IsAdmin())
