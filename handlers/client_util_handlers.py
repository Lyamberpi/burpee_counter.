from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import initializer
from handlers import admin_handlers
from transaction import RecordTransactions


async def help_command_message(message: types.Message):
    await message.answer(
        "Что умеет бот?\n\n"
        "приседания/squats 100 - добавить результат приседаний\n"
        "отжимания/push_ups 100 - добавить результат отжиманий\n"
        "/my_statistic - посмотреть свою статистику\n"
        "/statistic - посмотреть общую статистику")


class ClientUtilsHandler:
    record_transactions = RecordTransactions()
    top_p_men = "Топ отжимания мужчины"
    top_p_women = "Топ отжимания женщины"
    top_s_men = "Топ приседания мужчины"
    top_s_women = "Топ приседания женщины"

    async def help_command_handler(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            await help_command_message(message)
        if str(message.from_user.id) in [initializer.super_admin, initializer.admin1, initializer.admin2]:
            await admin_handlers.help_admin_command_message(message)

    async def my_statistic_handler(self, message: types.Message):
        user_id = message.from_user.id
        if user_id == message.chat.id:
            own_push_ups = self.record_transactions.get_common_user_result(user_id, 1)
            own_squats = self.record_transactions.get_common_user_result(user_id, 2)
            text = ""
            if own_push_ups:
                text += str(own_push_ups) + " отжимания👊\n"
            if own_squats:
                text += "Приседания: " + str(own_squats) + " 🦿\n"
            if own_push_ups:
                text += "Личный вклад: " + str(own_push_ups) + "/" + str(initializer.push_ups_goal) + " отжиманий👊\n"
            if own_squats:
                text += "Личный вклад: " + str(own_squats) + "/" + str(initializer.squats_goal) + " 🦿"
            if own_push_ups is None and own_squats is None:
                text = "Мало данных для составления статистики. Добавь свой результат и попробуй ещё раз!"
            await message.answer(text)

    async def statistic_handler(self, message: types.Message):
        user_id = message.from_user.id
        if user_id == message.chat.id:
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(InlineKeyboardButton(self.top_p_men, callback_data="top_p_men"),
                         InlineKeyboardButton(self.top_p_women, callback_data="top_p_women"))
            keyboard.add(InlineKeyboardButton(self.top_s_men, callback_data="top_s_men"),
                         InlineKeyboardButton(self.top_s_women, callback_data="top_s_women"))
            push_ups_result = str(self.record_transactions.get_common_result(1))
            squats_result = str(self.record_transactions.get_common_result(2))
            text = "Наши результаты\nОтжимания: " + push_ups_result + " Цель: " + str(
                initializer.push_ups_goal) + " 👊\nПриседания: " + squats_result + " Цель: " + str(
                initializer.squats_goal) + " 🦿"
            await message.answer(text, reply_markup=keyboard)

    async def push_ups_men(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_p_men + "👊</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 1, 1),
            parse_mode="HTML")

    async def push_ups_women(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_p_women + "👊</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 1, 2),
            parse_mode="HTML")

    async def squats_men(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_s_men + "🦿</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 2, 1),
            parse_mode="HTML")

    async def squats_women(self, callback: types.CallbackQuery):
        await callback.message.answer(
            "<b>" + self.top_s_women + "🦿</b>\n\n" + self.record_transactions.get_top(callback.from_user.id, 2, 2),
            parse_mode="HTML")
