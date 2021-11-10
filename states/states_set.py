from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    add_city = State()
    add_gender = State()
    add_age = State()


class AdminStates(StatesGroup):
    editing_records = State()


class DeleteStates(StatesGroup):
    deleting = State()


class FormTopStates(StatesGroup):
    set_gender = State()
    set_ex_type = State()
    set_date_from = State()
    set_date_to = State()


class EditTopStates(StatesGroup):
    add_photo = State()
    edit_top = State()
