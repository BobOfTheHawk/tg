from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()


class RoutineStates(StatesGroup):
    awaiting_routine_title = State()
    awaiting_routine_description = State()
    awaiting_routine_end_time = State()
    awaiting_routine_end_time1 = State()
    awaiting_new_end_time_minute = State()
    awaiting_routine_days = State()
    awaiting_new_title = State()
    awaiting_new_end_time = State()
    awaiting_new_days = State()
    awaiting_new_description = State()


class MoneyPlanes(StatesGroup):
    back = State()
    enter_amount = State()
    enter_days = State()


class MoneyPlane(StatesGroup):
    back = State()
    add_plan_name = State()
    add_plan_money = State()


class AddMoney(StatesGroup):
    name = State()
    money = State()
    plan_time = State()


class DownloadStates(StatesGroup):
    waiting_for_link = State()


class AddCodeState(StatesGroup):
    waiting_for_title = State()
    waiting_for_code = State()


class AddCategoryState(StatesGroup):
    name = State()
    photo = State()
    description = State()


class EditCategoryState(StatesGroup):
    select_category = State()
    edit_name = State()
    edit_photo = State()
    edit_description = State()