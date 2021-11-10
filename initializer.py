from os import environ

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import filters

import states
from handlers.edit_top_handlers import EditTopHandlers
from handlers.form_top_handlers import FormTopHandlers
from states import states_set
from handlers.admin_handlers import AdminHandlers
from handlers.client_util_handlers import ClientUtilsHandler
from handlers.exercise_handlers import ExerciseHandler
from handlers.registration_handlers import RegistrationHandler

run_goal = environ["RUN_GOAL"]
burpee_goal = environ["BURPEE_GOAL"]
super_admin = environ["SUPER_ADMIN"]


class Initializer:

    def __init__(self) -> None:
        self.bot = Bot(token=environ['BOT_TOKEN'])
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        exercise_handler = ExerciseHandler()
        registration_handler = RegistrationHandler()
        client_utils_handler = ClientUtilsHandler()
        admin_handler = AdminHandlers()
        form_top_handler = FormTopHandlers(self.bot)
        edit_top_handler = EditTopHandlers(self.bot)
        self.register_exercise_handlers(exercise_handler)
        self.register_registration_handlers(registration_handler)
        self.register_client_utils_handler(client_utils_handler)
        self.register_admin_handlers(admin_handler)
        self.register_form_top_handlers(form_top_handler)
        self.register_edit_top_handlers(edit_top_handler)

    def register_exercise_handlers(self, exercise_handler):
        self.dp.register_message_handler(exercise_handler.add_run_handler,
                                         filters.Text(startswith=["Бег", "Run"], ignore_case=True))
        self.dp.register_message_handler(exercise_handler.add_burpee_handler,
                                         filters.Text(startswith=["Берпи", "Бёрпи", "Burpee"], ignore_case=True))
        self.dp.register_message_handler(exercise_handler.add_team_result_handler, user_id=super_admin,
                                         commands=["add_team_result"])

    def register_registration_handlers(self, registration_handler):
        self.dp.register_message_handler(registration_handler.start_handler, commands=["start"])
        self.dp.register_message_handler(registration_handler.add_city_handler, state=states_set.Registration.add_city)
        self.dp.register_callback_query_handler(registration_handler.add_gender_handler,
                                                state=states_set.Registration.add_gender)
        self.dp.register_message_handler(registration_handler.add_age_handler, state=states_set.Registration.add_age)

    def register_client_utils_handler(self, client_utils_handler):
        self.dp.register_message_handler(client_utils_handler.help_command_handler, commands=["help"])
        self.dp.register_message_handler(client_utils_handler.my_statistic_handler, commands=["my_statistic"])
        self.dp.register_message_handler(client_utils_handler.statistic_handler, commands=["statistic"])
        self.dp.register_callback_query_handler(client_utils_handler.burpee_men, text="top_b_men")
        self.dp.register_callback_query_handler(client_utils_handler.burpee_women, text="top_b_women")
        self.dp.register_callback_query_handler(client_utils_handler.run_men, text="top_r_men")
        self.dp.register_callback_query_handler(client_utils_handler.run_women, text="top_r_women")

    def register_admin_handlers(self, admin_handler):
        self.dp.register_message_handler(admin_handler.set_zero_run_handler, user_id=super_admin,
                                         commands=["set_zero_run"])
        self.dp.register_message_handler(admin_handler.set_zero_burpee_handler, user_id=super_admin,
                                         commands=["set_zero_burpee"])
        self.dp.register_message_handler(admin_handler.ban_user, user_id=super_admin, commands=["ban"])
        self.dp.register_message_handler(admin_handler.unban_user, user_id=super_admin, commands=["unban"])
        self.dp.register_message_handler(admin_handler.show_records_handler, user_id=super_admin,
                                         commands=["show_records"])
        self.dp.register_message_handler(admin_handler.stop_edit_handler, user_id=super_admin,
                                         commands=["stop_edit"], state=states.AdminStates.editing_records)
        self.dp.register_message_handler(admin_handler.editing_records, user_id=super_admin,
                                         state=states.AdminStates.editing_records)
        self.dp.register_message_handler(admin_handler.help_admin_handler, user_id=super_admin,
                                         commands=["help_admin"])
        self.dp.register_callback_query_handler(admin_handler.delete_records_handler, user_id=super_admin,
                                                state=states.DeleteStates.deleting)
        self.dp.register_message_handler(admin_handler.add_chat_handler, user_id=super_admin,
                                         commands=["add_chat"])

    def register_form_top_handlers(self, form_top_handler):
        self.dp.register_message_handler(form_top_handler.form_top_handler, user_id=super_admin, commands=["form_top"])
        self.dp.register_callback_query_handler(form_top_handler.add_exercise_top_for_female_handler,
                                                user_id=super_admin, state=states.FormTopStates.set_gender,
                                                text="add_top_female")
        self.dp.register_callback_query_handler(form_top_handler.add_exercise_top_for_male_handler,
                                                user_id=super_admin, state=states.FormTopStates.set_gender,
                                                text="add_top_male")
        self.dp.register_callback_query_handler(form_top_handler.add_from_date_handler,
                                                filters.Text(startswith="add_top_ex_"), user_id=super_admin,
                                                state=states.FormTopStates.set_ex_type)
        self.dp.register_message_handler(form_top_handler.add_to_date_handler, user_id=super_admin,
                                         state=states.FormTopStates.set_date_from)
        self.dp.register_message_handler(form_top_handler.prepare_top, user_id=super_admin,
                                         state=states.FormTopStates.set_date_to)

    def register_edit_top_handlers(self, edit_top_handler):
        self.dp.register_callback_query_handler(edit_top_handler.add_photo_handler, user_id=super_admin,
                                                text="add_photo")
        self.dp.register_message_handler(edit_top_handler.validate_and_add_photo_handler, user_id=super_admin,
                                         content_types=["photo"], state=states.EditTopStates.add_photo)
        self.dp.register_callback_query_handler(edit_top_handler.stop_top_edit, user_id=super_admin, state="*",
                                                text="cancel_edit_top")
        self.dp.register_callback_query_handler(edit_top_handler.delete_photo, user_id=super_admin, text="del_photo")
        self.dp.register_callback_query_handler(edit_top_handler.edit_top_handler, user_id=super_admin, text="edit_top")
        self.dp.register_message_handler(edit_top_handler.process_edit, user_id=super_admin,
                                         state=states.EditTopStates.edit_top)
        self.dp.register_callback_query_handler(edit_top_handler.send_top_handler, user_id=super_admin, text="send_top")
        self.dp.register_callback_query_handler(edit_top_handler.process_send_top_handler,
                                                filters.Text(startswith="sendmsg_"), user_id=super_admin)
        self.dp.register_callback_query_handler(edit_top_handler.show_text_top_handler, user_id=super_admin,
                                                text="show_text_top")
        self.dp.register_callback_query_handler(edit_top_handler.delete_msg_handler, user_id=super_admin,
                                                text="del_msg")
