from os import environ

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.client_util_handlers import help_command_message
from models import User
from states import states_set
from transaction.transactions import UserTransactions


class RegistrationHandler:
    user_transactions = UserTransactions()

    async def start_handler(self, message: types.Message):
        user_age = self.user_transactions.get_user_age(message.from_user.id)
        if message.from_user.id == message.chat.id and user_age is None or (
                type(user_age) is tuple and user_age[0] is None):
            from_user = message.from_user
            user = User(from_user.first_name, from_user.last_name, from_user.id)
            self.user_transactions.add_user(user)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Да!", callback_data="add_city_question"))
            await message.answer("🥳 Добро пожаловать в вызов #ЛямБерпи 👊\n\n"
                                 "🎯Наша цель - коллективно выполнить 1 000 000 бёрпи"
                                 " и пробежать 🏃 100 000 километров до 1 декабря 2022 года.\n\n"
                                 "Принимай активное участие, приглашай друзей,"
                                 " становись лучшей версией себя и вдохновляй окружение.\n\n"
                                 "💥 Море мотивации получишь внутри чатов,"
                                 " где тебя ждут ЗОЖ единомышленники.\n\n"
                                 "Я буду внимательно считать твои результаты"
                                 " и за активность поощрять приятными подарками 🎁\n\n"
                                 "🙌 А теперь давай немного познакомимся!\n\n"
                                 "Готов (а)?", reply_markup=keyboard)

    async def add_city_question_handler(self, callback_query: types.CallbackQuery):
        user_age = self.user_transactions.get_user_age(callback_query.from_user.id)
        if user_age is None or (type(user_age) is tuple and user_age[0] is None):
            await states_set.Registration.add_city.set()
            await callback_query.message.answer("Напиши из какой ты страны и города в формате: Страна/Город")

    async def add_city_handler(self, message: types.Message):
        self.user_transactions.add_city(message.from_user.id, message.text)
        await states_set.Registration.add_gender.set()
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("М", callback_data="burpeeMan"),
                     InlineKeyboardButton("Ж", callback_data="burpeeWoman"))
        await message.answer("Выбери свой пол 🙋‍♂️💃", reply_markup=keyboard)

    async def add_gender_handler(self, callback_query: types.CallbackQuery, state: FSMContext):
        message = callback_query.message
        gender = None
        if callback_query.data.__eq__("burpeeMan"):
            gender = 1
        elif callback_query.data.__eq__("burpeeWoman"):
            gender = 2
        self.user_transactions.add_gender(message.chat.id, gender)
        await states_set.Registration.add_age.set()
        await message.answer("Укажи свой возраст")
        await state.update_data({"gender": gender})

    async def add_age_handler(self, message: types.Message, state: FSMContext):
        await state.finish()
        self.user_transactions.add_age(message.from_user.id, int(message.text))
        await message.answer("🥳 Твоя регистрация завершена.\n"
                             "Подписывайся на основной <a href='t.me/lyamberpi'>канал вызова</a>"
                             " и отмечай в сторисах инстаграм аккаунт со своими пробежками / выполнением бёрпи"
                             " 🤳📷 instagram.com/lyamberpi\n"
                             # f"А это 👉 <a href='{link}'>чат с единомышленниками</a>"
                             ,parse_mode="HTML")
        await help_command_message(message)
