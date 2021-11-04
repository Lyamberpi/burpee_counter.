from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from states import states_set
from models import User
from handlers.client_util_handlers import help_command_message
from transaction.transactions import UserTransactions


class RegistrationHandler:
    user_transactions = UserTransactions()

    async def start_handler(self, message: types.Message):
        user_age = self.user_transactions.get_user_age(message.from_user.id)
        if not message.chat.type.__eq__("group") and user_age is None or (
                type(user_age) is tuple and user_age[0] is None):
            from_user = message.from_user
            user = User(from_user.first_name, from_user.last_name, from_user.id)
            self.user_transactions.add_user(user)
            await states_set.Registration.add_city.set()
            await message.answer("Добро пожаловать!\nВыберете Город")

    async def add_city_handler(self, message: types.Message):
        self.user_transactions.add_city(message.from_user.id, message.text)
        await states_set.Registration.add_gender.set()
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("М", callback_data="burpeeMan"),
                     InlineKeyboardButton("Ж", callback_data="burpeeWoman"))
        await message.answer("Выберете пол", reply_markup=keyboard)

    async def add_gender_handler(self, callback_query: types.CallbackQuery):
        message = callback_query.message
        gender = None
        if callback_query.data.__eq__("burpeeMan"):
            gender = 1
        elif callback_query.data.__eq__("burpeeWoman"):
            gender = 2
        self.user_transactions.add_gender(message.chat.id, gender)
        await states_set.Registration.add_age.set()
        await message.answer("Сколько Вам лет?")

    async def add_age_handler(self, message: types.Message, state: FSMContext):
        await state.finish()
        self.user_transactions.add_age(message.from_user.id, int(message.text))
        await message.answer("Регестрация завершена!")
        await help_command_message(message)
