from datetime import datetime

from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import states
from transaction import RecordTransactions


class FormTopHandlers:
    records = RecordTransactions()

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def form_top_handler(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            await states.FormTopStates.set_gender.set()
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("М", callback_data="add_top_male"),
                         InlineKeyboardButton("Ж", callback_data="add_top_female"))
            await message.answer("Выберете пол", reply_markup=keyboard)

    async def add_exercise_top_for_male_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await states.FormTopStates.set_ex_type.set()
        await state.update_data({"gender": 1})
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Бёрпи", callback_data="add_top_ex_burpee"),
                     InlineKeyboardButton("Бег", callback_data="add_top_ex_run"))
        await callback.message.edit_text("Выберете упражнение", reply_markup=keyboard)

    async def add_exercise_top_for_female_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await states.FormTopStates.set_ex_type.set()
        await state.update_data({"gender": 2})
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Бёрпи", callback_data="add_top_ex_burpee"),
                     InlineKeyboardButton("Бег", callback_data="add_top_ex_run"))
        await callback.message.edit_text("Выберете упражнение", reply_markup=keyboard)

    async def add_from_date_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await states.FormTopStates.set_date_from.set()
        await callback.message.delete_reply_markup()
        await state.update_data({"origin_msg_id": callback.message.message_id})
        if callback.data == "add_top_ex_burpee":
            ex_type = 1
        else:
            ex_type = 2
        await callback.message.edit_text("Введите дату начала в формате: "
                                         "'год-день-месяц часы:минуты:секунды' (2021-10-29 19:08:09)")
        await state.update_data({"ex_type": ex_type})

    async def add_to_date_handler(self, message: types.Message, state: FSMContext):
        message_text = message.text
        try:
            dt_object = datetime.strptime(message_text, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            await message.answer("Неверный формат даты, попробуйте ещё раз")
            return
        await states.FormTopStates.set_date_to.set()
        await message.delete()
        await state.update_data({"from_date": dt_object})
        user_data = await state.get_data()
        origin_msg_id = user_data.get("origin_msg_id")
        await self.bot.edit_message_text(
            "Введите конечную дату в формате: 'год-день-месяц часы:минуты:секунды' (2021-10-29 19:08:09)",
            chat_id=message.from_user.id, message_id=origin_msg_id)

    async def prepare_top(self, message: types.Message, state: FSMContext):
        message_text = message.text
        try:
            dt_object = datetime.strptime(message_text, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            await message.answer("Неверный формат даты, попробуйте ещё раз")
            return
        user_data = await state.get_data()
        origin_msg_id = user_data.get("origin_msg_id")
        from_date = user_data.get("from_date")
        gender_id = user_data.get("gender")
        ex_type_id = user_data.get("ex_type")
        top = self.records.get_records_by_date(ex_type_id, gender_id, from_date, str(dt_object))
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("Добавить фото", callback_data="add_photo"))
        keyboard.add(InlineKeyboardButton("Редактировать", callback_data="edit_top"),
                     InlineKeyboardButton("Просмотреть", callback_data="show_text_top"))
        keyboard.add(InlineKeyboardButton("Отправить топ", callback_data="send_top"))
        await state.finish()
        await message.delete()
        await self.bot.edit_message_text(top, chat_id=message.from_user.id, message_id=origin_msg_id, parse_mode="HTML",
                                         reply_markup=keyboard)
