from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    add_city = State()
    add_gender = State()
    add_age = State()


class AdminStates(StatesGroup):
    editing_records = State()


class DeleteStates(StatesGroup):
    deleting = State()
