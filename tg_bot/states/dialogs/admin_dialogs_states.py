from aiogram.fsm.state import StatesGroup, State


class AdminModeMenuDialogSG(StatesGroup):
    start = State()
    exit = State()


class AdminModeBroadcastDialogSG(StatesGroup):
    start = State()
    check_text = State()
    edit_text = State()
    invalid_text = State()
    add_image_or_not = State()
    add_image = State()
    invalid_image = State()
    finish_view = State()
    finish_creation = State()

    input_schedule_time = State()
    check_schedule_time = State()
    scheduled_broadcast_registered = State()

    cancel = State()


class AdminModeScheduledJobsDialogSG(StatesGroup):
    start = State()
    broadcast_jobs = State()
    selected_broadcast_job = State()
    canceled_broadcast_job = State()
    other_jobs = State()
