from aiogram import types

from handlers.client_util_handlers import convert_km_to_m
from models import User
from transaction import ChatTransactions, RecordTransactions, UserTransactions


class ExerciseHandler:
    chat_transactions = ChatTransactions()
    record_transactions = RecordTransactions()
    user_transactions = UserTransactions()

    async def add_run_handler(self, message: types.Message):
        from_user = message.from_user
        user = User(from_user.first_name, from_user.last_name, from_user.id)
        contribution = message.text.split(" ", 2)[1]
        common_user_result, contribution_in_km, name_link = await self.__add_run_result(message, user, contribution)
        gender: tuple = self.user_transactions.get_user_gender(from_user.id)
        if gender[0] == 2:
            contribution_in_km = " пробежала " + str(contribution_in_km)
        else:
            contribution_in_km = " пробежал " + str(contribution_in_km)
        await message.answer(
            name_link + contribution_in_km + "/" + str(common_user_result) + " км!",
            parse_mode="Markdown")

    async def add_burpee_handler(self, message: types.Message):
        from_user = message.from_user
        user = User(from_user.first_name, from_user.last_name, from_user.id)
        contribution = int(message.text.split(" ", 2)[1])
        common_user_result, contribution, name_link = await self.__add_burpee_result(message, user, contribution)
        gender: tuple = self.user_transactions.get_user_gender(from_user.id)
        if gender[0] == 2:
            contribution = " сделала " + str(contribution)
        else:
            contribution = " сделал " + str(contribution)
        await message.answer(
            name_link + contribution + "/" + str(common_user_result) + " бёрпи!",
            parse_mode="Markdown")

    async def add_team_result_handler(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            args = message.get_args().split()
            if len(args) == 2:
                if args[0].lower() in ["берпи", "бёрпи", "burpee", "бëрпи"]:
                    ex_type_id = 1
                    contribution = int(args[1])
                elif args[0].lower() in ["бег", "run"]:
                    ex_type_id = 2
                    contribution = convert_km_to_m(args[1])
                else:
                    return
            self.record_transactions.create_record(contribution, ex_type_id, "39713971", None)
            await message.answer("Запись успешно добавлена")

    async def __add_run_result(self, message, user, contribution_in_km):
        self.user_transactions.add_user(user)
        contribution_in_m = convert_km_to_m(contribution_in_km)
        self.__handle_new_record(message, contribution_in_m, 2)
        name_link = self.__prepare_name_link(message)
        common_user_result = round(self.record_transactions.get_common_user_result(message.from_user.id, 2), 3)
        await message.delete()
        return common_user_result, contribution_in_km, name_link

    async def __add_burpee_result(self, message, user, contribution):
        self.user_transactions.add_user(user)
        self.__handle_new_record(message, contribution, 1)
        name_link = self.__prepare_name_link(message)
        common_user_result = self.record_transactions.get_common_user_result(message.from_user.id, 1)
        await message.delete()
        return common_user_result, contribution, name_link

    def __handle_new_record(self, message, contribution, exercise_type):
        user_id = message.from_user.id
        chat_id = message.chat.id
        if chat_id == user_id:
            chat_id = None
        self.record_transactions.create_record(contribution, exercise_type, user_id, chat_id)

    @staticmethod
    def __prepare_name_link(message):
        user_name = message.from_user.first_name
        last_name = message.from_user.last_name
        user_id = message.from_user.id
        if last_name:
            user_name = user_name + " " + last_name
        text = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
        return text
