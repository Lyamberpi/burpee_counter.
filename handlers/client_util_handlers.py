from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import initializer
from transaction import RecordTransactions


async def help_command_message(message: types.Message):
    await message.answer(
        "Some help text\nSome help text\nSome help text\nSome help text\nSome help text\nSome help text\n")


def convert_km_to_m(contribution_in_km):
    if contribution_in_km.__contains__("."):
        arr = contribution_in_km.split(".")
    else:
        arr = contribution_in_km.split(",")
    contribution_in_m = int(arr[0]) * 1000
    if len(arr) > 1:
        contribution_in_m += + int(float("0." + arr[1]) * 1000)
    return contribution_in_m


class ClientUtilsHandler:
    record_transactions = RecordTransactions()
    top_b_men = "Топ бёрпи мужчины"
    top_b_women = "Топ бёрпи женщины"
    top_r_men = "Топ бег мужчины"
    top_r_women = "Топ бег женщины"

    async def help_command_handler(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            await help_command_message(message)

    async def my_statistic_handler(self, message: types.Message):
        user_id = message.from_user.id
        if user_id == message.chat.id:
            own_burpee = self.record_transactions.get_common_user_result(user_id, 1)
            own_run = self.record_transactions.get_common_user_result(user_id, 2)
            text = ""
            if own_burpee:
                text += str(own_burpee) + " бёрпи👊\n"
            if own_run:
                text += "Пробежал " + str(own_run) + " км🏃\n"
            if own_burpee:
                text += "Личный вклад: " + str(own_burpee) + "/" + str(initializer.burpee_goal) + " бёрпи👊\n"
            if own_run:
                text += "Личный вклад: " + str(own_run) + "/" + str(initializer.run_goal) + " км🏃"
            if own_burpee is None and own_run is None:
                text = "Мало данных для составления статистики. Добавь свой результат и попробуй ещё раз!"
            await message.answer(text)

    async def statistic_handler(self, message: types.Message):
        user_id = message.from_user.id
        if user_id == message.chat.id:
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(InlineKeyboardButton(self.top_b_men, callback_data="top_b_men"),
                         InlineKeyboardButton(self.top_b_women, callback_data="top_b_women"))
            keyboard.add(InlineKeyboardButton(self.top_r_men, callback_data="top_r_men"),
                         InlineKeyboardButton(self.top_r_women, callback_data="top_r_women"))
            burpee_result = str(self.record_transactions.get_common_result(1))
            run_result = str(self.record_transactions.get_common_result(2))
            text = "Наши результаты\nБёрпи: " + burpee_result + " Цель: " + str(
                initializer.burpee_goal) + " 👊\nПробежали: " + run_result + "км Цель: " + str(
                initializer.run_goal) + " км🏃"
            await message.answer(text, reply_markup=keyboard)

    async def burpee_men(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_b_men + "👊</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 1, 1),
            parse_mode="HTML")

    async def burpee_women(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_b_women + "👊</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 1, 2),
            parse_mode="HTML")

    async def run_men(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_r_men + "🏃</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 2, 1),
            parse_mode="HTML")

    async def run_women(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_r_women + "🏃</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 2, 2),
            parse_mode="HTML")
