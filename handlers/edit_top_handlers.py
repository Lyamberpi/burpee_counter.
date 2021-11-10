from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

import states
from transaction import ChatTransactions


class EditTopHandlers:

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    chat_transactions = ChatTransactions()

    async def add_photo_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await states.EditTopStates.add_photo.set()
        await state.update_data({"origin_msg_id": callback.message.message_id})
        if callback.message.text:
            await state.update_data({"origin_msg_text": callback.message.text})
        else:
            await state.update_data({"origin_msg_text": callback.message.caption})
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel_edit_top"))
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    async def validate_and_add_photo_handler(self, message: types.Message, state: FSMContext):
        file = await self.__get_photo_from_message(message)
        user_data = await state.get_data()
        txt = user_data.get("origin_msg_text")
        await message.answer_photo(photo=file,
                                   caption=txt, reply_markup=self.__get_keyboard(True))
        await message.delete()
        await self.bot.delete_message(chat_id=message.from_user.id, message_id=user_data.get("origin_msg_id"))
        await state.finish()

    async def __get_photo_from_message(self, message):
        file_id = message.photo[-1].file_id
        file_info = await self.bot.get_file(file_id)
        url = await file_info.get_url()
        file = InputFile.from_url(url)
        return file

    async def stop_top_edit(self, callback: types.CallbackQuery, state: FSMContext):
        if callback.message.caption:
            with_photo = True
        else:
            with_photo = False
        await callback.message.edit_reply_markup(reply_markup=self.__get_keyboard(with_photo))
        await state.finish()

    async def delete_photo(self, callback: types.CallbackQuery):
        message_text = callback.message.caption
        await callback.message.delete()
        await callback.message.answer(message_text, reply_markup=self.__get_keyboard(False))

    async def edit_top_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await states.EditTopStates.edit_top.set()
        if callback.message.caption:
            with_photo = True
        else:
            with_photo = False
        await state.update_data({"origin_msg_id": callback.message.message_id, "with_photo": with_photo})
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel_edit_top"))
        await callback.message.edit_reply_markup(keyboard)

    async def process_edit(self, message: types.Message, state: FSMContext):
        user_date = await state.get_data()
        with_photo = user_date.get("with_photo")
        origin_msg_id = user_date.get("origin_msg_id")
        if with_photo:
            await self.bot.edit_message_caption(message.from_user.id, origin_msg_id, caption=message.text,
                                                reply_markup=self.__get_keyboard(True))
        else:
            await self.bot.edit_message_text(message.text, message_id=origin_msg_id, chat_id=message.from_user.id,
                                             reply_markup=self.__get_keyboard(True))
        await message.delete()
        await state.finish()

    async def send_top_handler(self, callback: types.CallbackQuery):
        chat_list: list = self.chat_transactions.get_all_chats()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for chat_id, title, gender in chat_list:
            keyboard.insert(InlineKeyboardButton(title, callback_data="sendmsg_" + str(chat_id)))
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel_edit_top"))
        await callback.message.edit_reply_markup(keyboard)

    async def process_send_top_handler(self, callback: types.CallbackQuery):
        chat_id = callback.data.split("_")[1]
        if callback.message.caption:
            photo = await self.__get_photo_from_message(callback.message)
            await self.bot.send_photo(chat_id, photo=photo, caption=callback.message.caption,
                                      parse_mode="HTML")
        else:
            await self.bot.send_message(chat_id, text=callback.message.text, parse_mode="HTML")
        await callback.message.answer(text="Сообщение отправлено")

    async def show_text_top_handler(self, callback: types.CallbackQuery):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Удалить пример", callback_data="del_msg"))
        if callback.message.caption:
            photo = await self.__get_photo_from_message(callback.message)
            await callback.message.answer_photo(photo=photo, caption=callback.message.caption, parse_mode="HTML",
                                                reply_markup=keyboard)
        else:
            await callback.message.answer(text=callback.message.text, parse_mode="HTML", reply_markup=keyboard)

    async def delete_msg_handler(self, callback: types.CallbackQuery):
        await callback.message.delete()

    @staticmethod
    def __get_keyboard(with_photo: bool):
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton("Добавить фото", callback_data="add_photo"))
        if with_photo:
            keyboard.insert(InlineKeyboardButton("Удалить фото", callback_data="del_photo"))
        keyboard.add(InlineKeyboardButton("Редактировать", callback_data="edit_top"),
                     InlineKeyboardButton("Просмотреть", callback_data="show_text_top"))
        keyboard.add(InlineKeyboardButton("Отправить топ", callback_data="send_top"))
        return keyboard
