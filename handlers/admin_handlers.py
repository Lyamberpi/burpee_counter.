from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import states
from handlers.client_util_handlers import convert_km_to_m
from transaction import RecordTransactions, UserTransactions


class AdminHandlers:
    record_transactions = RecordTransactions()
    user_transactions = UserTransactions()

    async def set_zero_run_handler(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Да", callback_data="2"), InlineKeyboardButton("Нет", callback_data="0"))
            await message.answer("Вы действительно ходите удалить все записи содержащие бёрпи?", reply_markup=keyboard)
            await states.DeleteStates.deleting.set()

    async def set_zero_burpee_handler(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Да", callback_data="1"), InlineKeyboardButton("Нет", callback_data="0"))
            await message.answer("Вы действительно ходите удалить все записи содержащие бёрпи?", reply_markup=keyboard)
            await states.DeleteStates.deleting.set()

    async def delete_records_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        if callback.data == "0":
            await callback.message.delete()
            return
        if callback.data == "1":
            await callback.message.delete()
            deleted_rows = self.record_transactions.delete_records_by_ex_type(1)
        else:
            deleted_rows = self.record_transactions.delete_records_by_ex_type(2)
        self.record_transactions.set_autoincrement(1)
        await callback.message.answer(str(deleted_rows) + " записей удалено успешно!")

    async def ban_user(self, message: types.Message):
        id_to_ban = int(message.get_args())
        if id_to_ban != message.from_user.id:
            self.user_transactions.ban_user(id_to_ban)
            await message.delete()
            await message.answer("[Пользователь](tg://user?id=" + str(id_to_ban) + ") забанен", parse_mode="Markdown")

    async def unban_user(self, message: types.Message):
        id_to_unban = int(message.get_args())
        if id_to_unban != message.from_user.id:
            self.user_transactions.unban_user(id_to_unban)
            await message.delete()
            await message.answer("[Пользователь](tg://user?id=" + str(id_to_unban) + ") разбанен",
                                 parse_mode="Markdown")

    async def show_records_handler(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            args = message.get_args()
            user_id, rows_number = args.split()
            if user_id == "all":
                record_list = self.record_transactions.show_all_records(int(rows_number))
            else:
                record_list = self.record_transactions.show_user_records(int(user_id), int(rows_number))
            message_text = "Вы находитесь в режиме редактирования\n" \
                           "<b>Для удаления записи</b> введите её номер\n" \
                           "<b>Для редактирования:</b> номер и новое значение\n" \
                           "<b>Для выхода</b> используйте команду /stop_edit\n\n" + self.__prepare_message(record_list,
                                                                                                           user_id)
            await states.AdminStates.editing_records.set()
            await message.answer(message_text, parse_mode="HTML")

    async def editing_records(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            user_message = message.text.split()
            record_id = user_message[0]
            await self.__edit_processing(message, record_id, user_message)

    async def stop_edit_handler(self, message: types.Message, state: FSMContext):
        await state.finish()
        await message.delete()
        await message.answer("Вы вышли из режима редактирования")

    async def help_admin_handler(self, message: types.Message):
        await message.answer(
            "/set_zero_run - обнулить счетчик бега\n"
            "/set_zero_burpee - обнулить счетчик бёрпи\n"
            "/ban user_id - забанить пользователя по его id\n"
            "/unban user_id - разбанить пользователя по его id\n"
            "/show_records user_id максимальное_количество_записей - показать записи пользователя по его id\n"
            "/show_records all максимальное_количество_записей - показать записи всех пользователей\n"
            "/add_team_result берпи/бёрпи/burpee - добавить запись бёрпи от имени администратора (Пользователь - "
            "Булава и команда)\n"
            "/add_team_result бег/run - добавить запись бега от имени администратора (Пользователь - "
            "Булава и команда)\n")

    async def __edit_processing(self, message, record_id, user_message):
        if len(user_message) > 1:
            value = user_message[1]
            exec_type = self.record_transactions.get_ex_type_buy_record_id(record_id)
            if exec_type is None:
                await self.__delete_and_answer(message, "Запись " + str(
                    record_id) + " <b>не существует.</b> Проверьте правильность введённых данных")
                return
            elif exec_type == 1:
                new_value = value
            else:
                new_value = convert_km_to_m(value)
            if self.record_transactions.update_record(record_id, new_value):
                await self.__delete_and_answer(message, "Запись " + str(
                    record_id) + " успешно обновлена, новое значение: " + str(value))
            else:
                await self.__delete_and_answer(message, "Запись " + str(
                    record_id) + " <b>не обновлена.</b> Проверьте правильность введённых данных")
        else:
            if self.record_transactions.delete_record(record_id):
                await self.__delete_and_answer(message, "Запись " + str(record_id) + " успешно удалена")
            else:
                await self.__delete_and_answer(message, "Запись " + str(
                    record_id) + " <b>не удалена.</b> Проверьте правильность введённых данных")

    async def __delete_and_answer(self, message, text):
        await message.delete()
        await message.answer(text, parse_mode="HTML")

    def __prepare_message(self, record_list, user_id):
        message_text = ""
        for record_id, first_name, second_name, exercise_type_id, contribution, gender in record_list:
            name = first_name
            if second_name:
                name += " " + second_name
            if exercise_type_id == 1:
                if gender == 2:
                    action = " сделала "
                else:
                    action = " сделал "
                units = " берпи"
            else:
                contribution = round(contribution / 1000, 3)
                if gender == 2:
                    action = " пробежала "
                else:
                    action = " пробежал "
                units = " км"
            href = '<a href="tg://user?id=' + str(user_id) + '">' + name + '</a>'
            line = str(record_id) + ". " + href + action + str(contribution) + units
            message_text += line + "\n"
        return message_text
